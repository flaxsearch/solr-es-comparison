import argparse
import requests
import re
import random
import time
import sys
import json


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
            query = []
            for j in xrange(args.nt):
                query.append(random.choice(words))
            numfound, t = search(query, random.choice(licenses))
            print >>f, numfound, t
            if i % 1000 == 0:
                print i, numfound, t

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
        
    t0 = time.time()
    resp = requests.get(args.solr, params=params)
    t1 = time.time()
    return (resp.json()['response']['numFound'], t1 - t0)

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

    # don't want json conversion in time
    jsonbody = json.dumps(body)

    t0 = time.time()
    resp = requests.post(args.es, jsonbody)
    t1 = time.time()

    jsonresp = resp.json()
    return (jsonresp['hits']['total'], t1 - t0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple load tester')
    parser.add_argument('--es', type=str, default=None, help="Elasticsearch search URL")
    parser.add_argument('--solr', type=str, default=None, help="Solr search URL")
    parser.add_argument('-i', type=str, required=True, help='input file for words')
    parser.add_argument('-o', type=str, required=True, help='output file')
    parser.add_argument('--ns', type=int, default=1, help='number of searches (default is 1)')
    parser.add_argument('--nt', type=int, default=1, help='number of terms (default is 1)')
    parser.add_argument('--nf', type=int, default=0, help='number of filters (default is 0)')
    parser.add_argument('--fac', default=False, action='store_true',
        help='use facets')

    args = parser.parse_args()

    if args.es is None and args.solr is None:
        print "Either --es or --solr is required"
        sys.exit(1)

    if args.es and args.solr:
        print "Cannot have both --es and --solr"
        sys.exit(1)
            
    main(search_es if args.es else search_solr)
        
