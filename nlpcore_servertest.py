# Instructies:
#
# 1. Download CoreNLP @ http://stanfordnlp.github.io/CoreNLP/ -> 'Download'
# 2. Extact de file naar een folder.
# 3. In een terminal in de folder, run
# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
# 4. Installeer py-corenlp met 'pip install pycorenlp'
# 5. Nu kun je deze file runnen.
# 6. Om de server af te sluiten:
# wget "localhost:9000/shutdown?key=`cat /tmp/corenlp.shutdown`" -O -
#
# Resources:
# http://stanfordnlp.github.io/CoreNLP/corenlp-server.html
# https://github.com/smilli/py-corenlp

from nltk.tree import *
from pycorenlp import StanfordCoreNLP
import time
nlp = StanfordCoreNLP('http://localhost:9000')
with open("testcorpus.txt", "r") as f:
    lines = list(f.read().splitlines())
for line in lines:
    parse = nlp.annotate(line, properties={
      'annotators': 'parse',
      'outputFormat': 'json'
      })
    print(Tree.fromstring(parse['sentences'][0]['parse']))
