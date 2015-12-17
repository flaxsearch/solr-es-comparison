# Python is perhaps not ideal for this, due to the GIL. However, if we assume 
# that the threads are mostly blocked on IO from the search engine, this should 
# be a relatively minor factor.

import argparse
import requests
import re
import random
import time
import sys
import json
import threading


def main(inpath, search):
    print 'Using seed: %s and threads: %s' % (args.seed, args.threads)
    random.seed(args.seed)

    words = set()
    with open(inpath) as f:
        for line in f:
            words.update(x.lower() for x in re.findall(r'\w{2,20}', line))

    # set up a list of 100 random licences so the engine can cache filter queries
    licenses = []
    for i in xrange(100):
        lics = []
        for j in xrange(3):
            lics.append((random.randint(1, 20), random.randint(1, 5)))
        licenses.append(lics)
    
    words = list(words)
    count = [0]

    def run_searches(threadnum):
        while True:
            search([random.choice(words) for n in xrange(3)], random.choice(licenses))
            count[0] += 1
    
    def qps_thread():
        while True:
            time.sleep(30.0)
            print count[0] / 30.0, 'qps'
            count[0] = 0
                
    for num in xrange(args.threads):
        print 'starting search thread', num
        thread = threading.Thread(target=run_searches, args=(num,))
        thread.start()
    
    threading.Thread(target=qps_thread).start()

def search_solr(q, lics):
    params = {'q': ' '.join(q), 'rows': '20', 'defType': 'edismax'}
    if lics:
        fq = []
        for lic in lics:
            fq.append('(+source:%d +level:[1 TO %d])' % lic)
        params['fq'] = ' '.join(fq)

    if args.fac:
        params['facet'] = 'true'
        params['facet.field'] = ['source', 'level']

    resp = requests.get(args.solr, params=params)
    if args.v:
        print 'Solr - total found:', resp.json()['response']['numFound']

def search_es(q, lics):
    fq = []    
    for lic in lics:
        fq.append({"bool": {"must": [
            {"term": {"source": lic[0]}},
            {"range": {"level": {"gte": 1, "lte": lic[1]}}}
        ]}})

    body = {
        "size": 20,
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "should": [f for f in fq]
                    }
                },
                "query": {
                    "match": {"text": ' '.join(q)}
                }
            }
        }
    }

    if args.fac:
        body["aggs"] = {
            "levels": {"terms": {"field": "level"}},
            "sources": {"terms": {"field": "source"}}
        }

    # JSON encoding included in timings, but significance doubtful
    # (can do over 46k encodes/s with 16 threads on m4.xlarge)
    resp = requests.post(args.es, json.dumps(body))
    if args.v:
        print 'ES - total found:', resp.json()['hits']['total']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple load tester')
    parser.add_argument('--es', type=str, default=None, help="Elasticsearch search URL")
    parser.add_argument('--solr', type=str, default=None, help="Solr search URL")
    parser.add_argument('-i', type=str, required=True, help='input file for words')
    parser.add_argument('--seed', type=long, default=long(time.mktime(time.gmtime())), help='seed value')
    parser.add_argument('--threads', type=long, default=1, help='threads')
    parser.add_argument('--fac', default=False, action='store_true', help='use facets')
    parser.add_argument('-v', default=False, action='store_true', help='verbose')

    args = parser.parse_args()

    if args.es is None and args.solr is None:
        print "Either --es or --solr is required"
        sys.exit(1)

    if args.es and args.solr:
        print "Cannot have both --es and --solr"
        sys.exit(1)

    main(args.i, search_es if args.es else search_solr)
        
