import sys
import gzip
import requests
import json

SOLR_URL = 'http://localhost:8983/solr/update'


def main():
    with gzip.open(sys.argv[1]) as f:
        body = []
        for count, line in enumerate(f):
            doc = json.loads(line)
            doc['id'] = sys.argv[2] + doc['id']
            body.append(json.dumps(doc))
            if count % 100 == 0:
                resp = requests.post(SOLR_URL,
                    headers={'Content-Type': 'application/json'},
                    data='[{0}]'.format(','.join(body)))
                assert resp.status_code == 200, resp.text
                print count
                body = []

    if body:
        resp = requests.post(SOLR_URL,
            headers={'Content-Type': 'application/json'},
            data='[{0}]'.format(','.join(body)))
            
    resp = requests.get(SOLR_URL + '?commit=true')
    assert resp.status_code == 200, resp.text

if __name__ == '__main__':
    main()

