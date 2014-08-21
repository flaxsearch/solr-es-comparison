import sys
import gzip
import requests

SOLR_URL = 'http://localhost:8983/solr/speedtest/update'


def main():
    with gzip.open(sys.argv[1]) as f:
        body = []
        for count, line in enumerate(f):
            body.append(line)
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

