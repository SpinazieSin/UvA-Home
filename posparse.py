# -*-coding:utf-8-*-
"""Part of speech (POS) tagging natural (news) language parser class file for the media understanding 2017 project.

File name: article.py
Author: Media Undertanding 2017
Date created: 7/2/2017
Date last modified: 7/2/2017
Python Version: 3.6
"""

from nltk.parse.stanford import StanfordParser

class POSParse():
    """
    Class for studying grammatical categories and their referents within news queries, which is then
    able to select an appropriate response."

    """
    
    def __init__(self):
        self.parser=StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
        
    # Private function
    def _find_NP_Leaves(self, t):

#        def filt(x):
#            print(x.label(), x.height())
#            return x.label()=='NP'

        # Generate subtrees at the lowest 'NP' node
        for subtree in t.subtrees(filter=lambda t: t.label()=='NP' and t.height()==3):
#        for subtree in t.subtrees(filter=filt):
            print(subtree)

    # The NLP equivalent of processCommand from chatengine.py
    def process_query(self, query):
        ptree = list(self.parser.raw_parse(query))[0]
        self._find_NP_Leaves(ptree)

