import argparse
import requests
import re
import random
import time
import json

SOLR_SEARCH = 'http://localhost:8983/solr/speedtest/query'
ES_SEARCH = 'http://localhost:9200/speedtest/_search'



def main(inpath, outpath, numsearches, search):
    words = set()
    with open(inpath) as f:
        for line in f:
            words.update(x.lower() for x in re.findall(r'\w{2,20}', line))

    # set up a list of 100 random licences so the engine can cache filter queries
    licenses = []
    for i in xrange(100):
        lics = []
        for j in xrange(random.randint(3, 10)):
            lics.append((random.randint(1, 20), random.randint(1, 5)))
        licenses.append(lics)
    
    words = list(words)
    with open(outpath, 'w') as f:
        for i in xrange(numsearches):
            t0 = time.time()
            numfound = search(random.choice(words), random.choice(licenses))
            t1 = time.time()
            print >>f, numfound, t1 - t0
            if i % 1000 == 0:
                print i, numfound, t1 - t0

def search_solr(q, lics):
    fq = []
    for lic in lics:
        fq.append('(source:%d AND level:[1 TO %d])' % lic)
    fq = ' OR '.join(fq)    
    resp = requests.get(SOLR_SEARCH, params={'q': q, 'fq': fq, 'rows': '0'})
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
            
    body = json.dumps({
        "query": {
            "filtered": {
                "query": {"match": {"text": q}},
                "filter": {"or": fq }
            }
        },
        "size": 0
    })

    resp = requests.post(ES_SEARCH, body)
    return resp.json()['hits']['total']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple load tester')
    parser.add_argument('--es', default=False, action='store_true',
        help='use Elasticsearch (defaults to Solr)')
    parser.add_argument('-i', type=str, required=True, help='input file for words')
    parser.add_argument('-o', type=str, required=True, help='output file')
    parser.add_argument('-n', type=int, required=True, help='number of searches')

    args = parser.parse_args()
    main(args.i, args.o, args.n, search_es if args.es else search_solr)
        