import sys
import gzip
import json
import requests

ES_URL = 'http://localhost:9200/speedtest/_bulk'


def main():
    with gzip.open(sys.argv[1]) as f:
        batch = []
        count = 0
        skip = int(sys.argv[3]) if len(sys.argv) == 4 else 0
        for line in f:
            count += 1
            if count > skip:
                doc = json.loads(line)
                batch.append(json.dumps({"index": 
                    {"_index": "speedtest", 
                     "_type": "document", 
                     "_id": "{0}{1}".format(sys.argv[2], doc["id"])}}))
                batch.append(line.strip())

                if count % 100 == 0:
                    print count
                    resp = requests.post(ES_URL,
                        headers={'Content-Type': 'application/octet-stream'},
                        data='\n'.join(batch) + "\n")
                    assert resp.status_code == 200, (resp.status_code, resp.text)
                    batch = []
            else:
                if count % 1000 == 0:
                    print 'skipped', count

if __name__ == '__main__':
    main()

