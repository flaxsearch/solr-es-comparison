import sys
import gzip
import json
import requests

ES_URL = 'http://localhost:9200/speedtest/'


def main():
    with gzip.open(sys.argv[1]) as f:
        for count, line in enumerate(f):
            doc = json.loads(line)
            resp = requests.post("{0}{1}".format(ES_URL, doc['id']),
                headers={'Content-Type': 'application/json'},
                data=line)
            assert resp.status_code == 201, (resp.status_code, resp.text)
            if count % 1000 == 0:
                print count

if __name__ == '__main__':
    main()

