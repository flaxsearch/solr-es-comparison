SolrCloud/Elasticsearch comparison tools
========================================
This repository contains various Python scripts and config files used by Flax for our
performance comparison of Solr and Elasticsearch, presented at the BCS Search Solutions 
event in November 2014 - the slides for which are at:

http://www.slideshare.net/charliejuggler/lucene-solrlondonug-meetup28nov2014-solr-es-performance

These files are provided for interest only, and we make no claims about their usefulness 
for any other application.

In order to provide a completely "fair" comparison, the exact same document set is used 
for both the Solr and Elasticsearch indexes. To avoid the overhead involved in downloading
a large document set, we instead used a Markov chain (and a Python implementation by 
Shabda Raaj) to generate random documents of various sizes from a training document.
Our study used data/stoicism.txt (downloaded from gutenberg.org) for training, but any
"normal" text of reasonable size and should be usable for this. One thing that is currently
unclear is how realistic this approach is compared with real documents, but Elasticsearch
and Solr did at least receive the same data. Analysis also showed that the Markov-generated 
text (like natural text) obeyed Zipf's Law on word distribution, which supports its 
validity.

Generating random documents
---------------------------
The `generate/generator.py` script is used to generate random documents for indexing,
which it saves as a gzip file. It takes the following arguments:

    -h, --help  show this help message and exit
    -n N        number of documents to generate
    -o O        output filename
    -i I        training text
    --min MIN   minimum doc size in words
    --max MAX   maximum doc size in words

e.g., to create 1M random documents ranging in size between 10 and 1000 words, based on
`data/stoicism.txt`:

    $ cd generate
    $ python -n 1000000 -i ../data/stoicism.txt -o ../data/docs.gz --min 10 --max 1000

Indexing to Elasticsearch
-------------------------
Before indexing, you need to configure the index, e.g. with curl:

    $ cd elasticsearch
    $ curl -XPUT http://localhost:9200/speedtest -d@index-config.json

(replacing localhost:9200 with the location of your Elasticsearch instance). Then edit the
`indexer.py` script and set `ES_URL` to point to the speedtest index. 

    $ time python indexer.py ../data/docs.gz A

The second parameter (A in this case) is used as an ID prefix. You can run several indexers
in parallel, using different ID prefixes to prevent ID clashes.

Indexing to Solr
----------------
A solr `conf` directory is provided in `solr`. You will need to upload this to SolrCloud 
using the usual methods (or for single node Solr, copy it over the default config). The
`indexer.py` script needs to be edited to point `SOLR_URL` to the correct location. Then,
the indexer is run in the same way as the Elasticsearch indexer.

Running the search tests
------------------------
The main test script is `loadtester.py` in `loadtest`. It takes the arguments:

    -h, --help   show help message and exit
    --es ES      Elasticsearch search URL
    --solr SOLR  Solr search URL
    -i I         input file for words
    -o O         output file
    --ns NS      number of searches (default is 1)
    --nt NT      number of terms (default is 1)
    --nf NF      number of filters (default is 0)
    --fac        use facets

For example:

    $ python loadtester.py \
        --solr "http://localhost:8983/solr/collection1/query" \
        -i ../data/stoicism.txt -o test1.txt --ns 100 --nt 3

The output is simply a text file where each line records the number of documents found
and the query time. To get some basic analysis of the results:

    $ python analyser.py test1.txt
    
The `merge2.py` and `merge3.py` scripts can be used to merge the query times of two or 
three results files and write them as a .cvs file for importing into a spreadsheet etc.

The `qps.py` script runs searches repeatedly and prints the QPS to stdout. Multiple 
instances can be run concurrently to increase the load (there is no multithreading,
currently).




