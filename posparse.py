# -*-coding:utf-8-*-
"""Part of speech (POS) tagging natural (news) language parser class file for the media understanding 2017 project.

File name: article.py
Author: Media Undertanding 2017
Date created: 7/2/2017
Date last modified: 7/2/2017
Python Version: 3.6
"""

from nltk.parse.stanford import StanfordParser
import datefinder
import newsextractor
import userprofile
from datetime import datetime, timedelta

class POSParse(object):
    """
    Class for studying grammatical categories and their referents within news queries, which is then
    able to select an appropriate response."

    """

    def __init__(self):
        self.parser=StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz", java_options='-mx3000m')
        # tagger is used for named entity recognition
        # Potential tags are Location, Person and Organization
#        self.tagger = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')
        self.source_ents = self.source_entities()
        self.place_ents = self.place_entities()
        self.categories = userprofile.UserProfile().interests.keys()

        date_terminals = {"days", "months", "weeks"}
        date_words = ["first", "second", "third",
        "fourth","fifth","sixth","seventh","eighth","nineth", "tenth",
        "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth"]
        count_words = ["two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "thirteen", "fourteen"]
        count_numbers = set(range(1,31))
        months = {"january","february","march","april","may","june","july","august",
        "september","october","november","december"}
        self.date_phrases = {"yesterday", "today", "recent", "last day", "last week", "last month",
        "one day ago", "one month ago", "one week ago", "right now", "now"}
        for m in months:
            self.date_phrases.update([m + " " + d for d in date_words])
        for c in count_words:
            self.date_phrases.update([c + " " + d + " ago" for d in date_terminals])
        for d in date_terminals:
            self.date_phrases.update(["last " + str(c) + " " + d for c in count_numbers])
            self.date_phrases.update(["last " + c + " " + d for c in count_words])

        self.to_int = {elem : i + 1 for (i, elem) in enumerate(date_words)}
        self.to_int.update({elem : i + 2 for (i, elem) in enumerate(count_words)})

        # maybe updates is a keywords in some contextes?
        self.non_keywords = {"news", "i", "updates", "me", "you"}

    # The NLP equivalent of processCommand from chatengine.py
    def process_query(self, query):
        ptree = list(self.parser.raw_parse(query))[0]
        # search is the command the chat enging has to carry out.
        # Maybe add ways to differentiate if the user wants news or not
        cmd = "present_news"
        args = self.process_tree(ptree)
        return cmd, args


    def process_queries(self, queries):
        ptrees = self.parser.raw_parse_sents(queries)
        for ptree, query in zip(ptrees, queries):
            print("------------")
            print(query)
            self.process_tree(list(ptree)[0])

    def process_tree(self, tree, debug=False):
        np_trees = self._find_NP_Leaves(tree)
        nps = {" ".join(t.leaves()).lower() for t in np_trees}
        nps = {np[4:] if np[:3] == 'the' else np for np in nps}
        if debug:
            print("NPs", list(nps))
        # see if NPs contain places or news sources
        sources = {np for np in nps if np in self.source_ents}
        places = {np for np in nps if np in self.place_ents}
        dates = {self.to_datetime(np) np for np in nps if self.find_dates(np)}
        cats = {np for np in nps if np in self.categories}
        nps -= sources | dates | places | cats # union

        keywords = {np for np in nps if not len(set(np.split(" ")) & self.non_keywords)} # no commons
        if debug:
            print("sources:", list(sources))
            print("places", list(places))
            print("dates:", list(dates))
            print("keywords:", list(keywords))
            print("categories:", list(cats))
        # dictionary get like operator for list
        get = lambda l, i: None if i > len(l)-1 else list(l)[i] 
#        return get(keywords,0), get(dates,0), get(dates,1), get(places,0), get(sources,0)
        # maybe create this list dynamically?
        return [{"search_term" : get(keywords,0),  "date1" : get(dates, 0),  
        "date2" : get(dates,1), "place": get(places,0), "sources" : get(sources,0)}]
        

    # Function that asks the news extractor for it's sources
    def source_entities(self):
        return newsextractor.NewsExtractor().supported_news_papers

   # Returns a fast super fast trie datastructure of place entities
    def place_entities(self):
        with open("Places/BigListOfPlaces.txt", "r") as f:
            return set(f.read().splitlines())

    def find_dates(self, np):
        dates = list(datefinder.find_dates(np))
        if len(dates) > 0:
            return True
        else:
            return np in self.date_phrases


    # Private function
    def _find_NP_Leaves(self, t):
        # Generate subtrees at the lowest 'NP' node
        return t.subtrees(filter=lambda t: t.label()=='NP' and t.height()==3)

if __name__ == "__main__":
    with open("testcorpus.txt", "r") as f:
        questions = f.read().splitlines()
        parser = POSParse()
        parser.process_queries(questions)
#        for q in questions:
#            print("------------")
#            print(q)
#            parser.process_query(q)
