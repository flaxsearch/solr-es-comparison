import argparse
import requests
import re
import random
import time
import sys
import json


def main(inpath, search):
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
    while True:
        t0 = time.time()
        for i in xrange(100):
            numfound = search(
                [random.choice(words), random.choice(words), random.choice(words)], 
                random.choice(licenses))
        print 100 / (time.time() - t0), 'qps'

def search_solr(q, lics):
    fq = []
    for lic in lics:
        fq.append('(source:%d AND level:[1 TO %d])' % lic)
    fq = ' OR '.join(fq)
    q = ' OR '.join(q)

    resp = requests.get(args.solr, params={'q': q, 'fq': fq, 'rows': '10'})
    return resp.json()['response']['numFound']

def search_es(q, lics):
    fq = []    
    for lic in lics:
        fq.append(
            {"and": [
                {"term": {"source": lic[0]}},
                {"numeric_range": {"level": {"gte": 1, "lte": lic[1]}}}
            ]})

    body = {
        "query": {
            "filtered": {
                "filter": {"or": fq },
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"text": x}} for x in q
                        ]
                    }
                }
            }
        },
        "size": 10,
    }

    resp = requests.post(args.es, json.dumps(body))
    return resp.json()['hits']['total']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple load tester')
    parser.add_argument('--es', type=str, default=None, help="Elasticsearch search URL")
    parser.add_argument('--solr', type=str, default=None, help="Solr search URL")
    parser.add_argument('-i', type=str, required=True, help='input file for words')

    args = parser.parse_args()

    if args.es is None and args.solr is None:
        print "Either --es or --solr is required"
        sys.exit(1)

    if args.es and args.solr:
        print "Cannot have both --es and --solr"
        sys.exit(1)

    main(args.i, search_es if args.es else search_solr)
        
