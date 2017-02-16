# -*-coding:utf-8-*-
"""Part of speech (POS) tagging natural (news) language parser class file for the media understanding 2017 project.

File name: article.py
Author: Media Undertanding 2017
Date created: 7/2/2017
Date last modified: 7/2/2017
Python Version: 3.6
"""

from nltk.parse.stanford import StanfordParser
from nltk.tag import StanfordNERTagger
from .. import newsextractor

class POSParse():
    """
    Class for studying grammatical categories and their referents within news queries, which is then
    able to select an appropriate response."

    """
    
    def __init__(self):
        self.parser=StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
        # tagger is used for named entity recognition
        # Potential tags are Location, Person and Organization
#        self.tagger = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')
        self.source_ents = self.source_entities()
        self.place_ents = self.place_entities()
        
    # The NLP equivalent of processCommand from chatengine.py
    def process_query(self, query):
        ptree = list(self.parser.raw_parse(query))[0]
        np_trees = self._find_NP_Leaves(ptree)
        nps = [t.leaves() for t in np_trees]
        print(nps)
        # see if Nps contain places
        sources = [np for np in nps if np in self.source_ents]
        places = [np for np in nps if np in self.place_ents]
        print("sources:", sources)
        print("", places)
        
    # Function that asks the news extractor for it's sources
    def source_entities(self):
        return newsextractor.NewsExtractor().supported_news_papers
   
   # Returns a fast super fast trie datastructure of place entities
    def place_entities(self):
        with open("Places/BigListOfPlaces.txt", "r") as f:
            return set(f.read().splitlines())
        
    # Private function
    def _find_NP_Leaves(self, t):
        # Generate subtrees at the lowest 'NP' node
        return t.subtrees(filter=lambda t: t.label()=='NP' and t.height()==3)
        
        
if __name__ == "__main__":
    with open("QAmodule/testcorpus.txt", "r") as f:
        questions = f.read().splitlines()
        parser = POSparse()
        for q in questions:
            parser.process_query(q)
            
    
    
    
    
    
    
    
    
    
    