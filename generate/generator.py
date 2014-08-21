import sys
import random
import gzip
import json
import argparse
import markov


def main(inpath, outpath, numdocs, minwords, maxwords):
    with open(inpath) as f:
        generator = markov.Markov(f)
    
    with gzip.open(outpath, 'w') as f:
        for i in xrange(numdocs):
            if i % 1000 == 0:
                print i
            json.dump({"text": generator.generate_markov_text(
                random.randint(minwords, maxwords)),
                "level": random.randint(1, 5),
                "source": random.randint(1, 20),
                "id": i
                }, f)
            f.write('\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate random documents')
    parser.add_argument('-n', type=int, default=100, 
        help='number of documents to generate')
    parser.add_argument('-o', type=str, default='out.gz',
        help='output filename')
    parser.add_argument('-i', type=str, required=True,
        help='training text')
    parser.add_argument('--min', type=int, default=100, 
        help='minimum doc size in words')
    parser.add_argument('--max', type=int, default=100, 
        help='maximum doc size in words')
    
    args = parser.parse_args()
    main(args.i, args.o, args.n, args.min, args.max)
        
