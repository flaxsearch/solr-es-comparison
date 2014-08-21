import sys
import gzip
import requests

SOLR_URL = 'http://localhost:8983/solr/speedtest/update'


def main():
    with gzip.open(sys.argv[1]) as f:
        for count, line in enumerate(f):
            body = '[{0}]'.format(line)
            resp = requests.post(SOLR_URL,
                headers={'Content-Type': 'application/json'},
                data=body)
            assert resp.status_code == 200, resp.text
            if count % 1000 == 0:
                print count
    resp = requests.get(SOLR_URL + '?commit=true')
    assert resp.status_code == 200, resp.text

if __name__ == '__main__':
    main()

