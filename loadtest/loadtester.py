import argparse
import requests
import re
import random
import time
import sys
import json

# configure your search URLs here
SOLR_SEARCH = 'http://localhost:8983/solr/query'
ES_SEARCH = 'http://localhost:9200/speedtest/_search'


def main(search):
    words = set()
    with open(args.i) as f:
        for line in f:
            words.update(x.lower() for x in re.findall(r'\w{2,20}', line))

    # set up a list of 100 random licences so the engine can cache filter queries
    licenses = []
    for i in xrange(100):
        lics = []
        for j in xrange(args.nf):
            lics.append((random.randint(1, 20), random.randint(1, 5)))
        licenses.append(lics)
    
    words = list(words)
    with open(args.o, 'w') as f:
        for i in xrange(args.ns):
            t0 = time.time()
            query = []
            for j in xrange(args.nt):
                query.append(random.choice(words))
            numfound = search(query, random.choice(licenses))
            t1 = time.time()
            print >>f, numfound, t1 - t0
            if i % 1000 == 0:
                print i, numfound, t1 - t0

def search_solr(q, lics):
    params = {'q': ' OR '.join(q), 'rows': '10'}
    if lics:
        fq = []
        for lic in lics:
            fq.append('(source:%d AND level:[1 TO %d])' % lic)
        params['fq'] = ' OR '.join(fq)

    if args.fac:
        params['facet'] = 'true'
        params['facet.field'] = ['source', 'level']
        
    resp = requests.get(SOLR_SEARCH, params=params)
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
        "size": 10,
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
        }
    }

    if args.fac:
        body["aggs"] = {
            "levels": {"terms": {"field": "level"}},
            "sources": {"terms": {"field": "source"}}
        }

    resp = requests.post(ES_SEARCH, json.dumps(body))
    return resp.json()['hits']['total']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple load tester')
    parser.add_argument('--es', default=False, action='store_true',
        help='use Elasticsearch (defaults to Solr)')
    parser.add_argument('-i', type=str, required=True, help='input file for words')
    parser.add_argument('-o', type=str, required=True, help='output file')
    parser.add_argument('--ns', type=int, required=True, help='number of searches')
    parser.add_argument('--nt', type=int, default=1, help='number of terms')
    parser.add_argument('--nf', type=int, default=0, help='number of filters (default is 0)')
    parser.add_argument('--fac', default=False, action='store_true',
        help='use facets')

    args = parser.parse_args()
    main(search_es if args.es else search_solr)
        
