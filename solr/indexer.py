import sys
import gzip
import requests
import json

SOLR_URL = 'http://84.40.61.82:8983/solr/update'


def main():
    with gzip.open(sys.argv[1]) as f:
        body = []
        for count, line in enumerate(f):
            doc = json.loads(line)
            doc['id'] = '{0}{1}'.format(sys.argv[2], doc['id'])
            body.append(json.dumps(doc))
            if count % 100 == 0:
                resp = requests.post(SOLR_URL,
                    headers={'Content-Type': 'application/json'},
                    data='[{0}]'.format(','.join(body)))
                assert resp.status_code == 200, resp.text
                body = []

            if count % 1000 == 0:
                print count

            if count % 100000 == 0:
                resp = requests.get(SOLR_URL + '?commit=true')
                assert resp.status_code == 200, resp.text

    if body:
        resp = requests.post(SOLR_URL,
            headers={'Content-Type': 'application/json'},
            data='[{0}]'.format(','.join(body)))
            
    resp = requests.get(SOLR_URL + '?commit=true')
    assert resp.status_code == 200, resp.text

if __name__ == '__main__':
    main()

