import sys
import gzip
import json
import requests

ES_URL = 'http://localhost:9200/speedtest/_bulk'


def main():
    with gzip.open(sys.argv[1]) as f:
        batch = []
        count = 0
        for line in f:
            doc = json.loads(line)
            batch.append(json.dumps({"index": 
                {"_index": "speedtest", "_type": "document", "_id": doc["id"]}}))
            batch.append(line.strip())

            count += 1
            if count % 100 == 0:
                print count
                resp = requests.post(ES_URL,
                    headers={'Content-Type': 'application/octet-stream'},
                    data='\n'.join(batch) + "\n")
                assert resp.status_code == 200, (resp.status_code, resp.text)
                batch = []

if __name__ == '__main__':
    main()

