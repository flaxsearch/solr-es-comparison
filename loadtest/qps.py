import argparse
import requests
import re
import random
import time
import sys
import json

SOLR_SEARCH = 'http://84.40.61.82:8983/solr/query'
ES_SEARCH = 'http://84.40.61.82:9200/speedtest/_search'



def main(inpath, search):
    words = set()
    with open(inpath) as f:
        for line in f:
            words.update(x.lower() for x in re.findall(r'\w{2,20}', line))

    # set up a list of 100 random licences so the engine can cache filter queries
    licenses = []
    for i in xrange(100):
        lics = []
        for j in xrange(1):
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

    resp = requests.get(SOLR_SEARCH, params={'q': q, 'fq': fq, 'rows': '10'})

    assert resp.status_code == 200, resp.text
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
#        "aggs": {
#            "levels": {"terms": {"field": "level"}},
#            "sources": {"terms": {"field": "source"}}
#        },
        "size": 10,
    }

    resp = requests.post(ES_SEARCH, json.dumps(body))
    return resp.json()['hits']['total']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple load tester')
    parser.add_argument('--es', default=False, action='store_true',
        help='use Elasticsearch (defaults to Solr)')
    parser.add_argument('-i', type=str, required=True, help='input file for words')

    args = parser.parse_args()
    main(args.i, search_es if args.es else search_solr)
        
