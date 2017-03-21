2# -*-coding:utf-8-*-
"""Part of speech (POS) tagging natural (news) language parser class file for the media understanding 2017 project.

File name: article.py
Author: Media Undertanding 2017
Date created: 7/2/2017
Date last modified: 7/2/2017
Python Version: 3.6
"""

#from nltk.parse.stanford import StanfordParser
import datefinder
import newsextractor
import userprofile
from datetime import datetime, timedelta

from nltk.tree import *
from pycorenlp import StanfordCoreNLP
import time

class POSParse(object):
    """
    Class for studying grammatical categories and their referents within news queries, which is then
    able to select an appropriate response."

    """

    def __init__(self):
        # Replaced with server implementation, should remove at some point. self.parser=StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz", java_options='-mx3000m')

        # Connect to local NLPcore server.
        self.parser=StanfordCoreNLP('http://localhost:9000')

        # tagger is used for named entity recognition
        # Potential tags are Location, Person and Organization
#        self.tagger = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')
        self.source_ents = self.source_entities()
        self.place_ents = self.place_entities()
        self.categories = userprofile.UserProfile().interests.keys()

        date_terminals = {"days", "months", "weeks"}
        date_words = ["first", "second", "third",
        "fourth","fifth","sixth","seventh","eighth","nineth", "tenth",
        "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth", "nineteenth", "twentieth",
        "twenty-first", "twenty-second", "twenty-third", "twenty-fourth",
        "twenty-fifth", "twenty-sixth", "twenty-seventh", "twenty-eight",
        "twenty-nineth", "thirtieth", "thirty-first"]
        count_words = ["two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
        "eleven", "twelve", "thirteen", "fourteen"]
        count_numbers = set(range(1,31))
        months = ["january","february","march","april","may","june","july","august",
        "september","october","november","december"]
        self.date_phrases = {"yesterday", "today", "recent", "last day", "last week", "last month",
        "one day ago", "one month ago", "one week ago", "right now", "now"}
        self.special_phrases = set(self.date_phrases) # Make a shallow copy.
        self.translate = {
            "recent" : "one months ago",
            "now" : "now",
            "right now" : "now",
            "today" : "now",
            "one day ago" : "one days ago",
            "one week ago" : "one weeks ago",
            "one month ago" : "one months ago",
            "yesterday" : "one days ago",
            "last day" : "one days ago",
            "last week" : "one weeks ago",
            "last month" : "one months ago"
        }
        self.translate.update({
            d + " of " + m : m + " " + d for d in date_words
                                         for m in months
        })
        for m in months:
            self.date_phrases.update([m + " " + d for d in date_words])
            self.date_phrases.update([d + " of " + m for d in date_words])
        for c in count_words:
            self.date_phrases.update([c + " " + d + " ago" for d in date_terminals])
        for d in date_terminals:
            self.date_phrases.update(["last " + str(c) + " " + d for c in count_numbers])
            self.date_phrases.update(["last " + c + " " + d for c in count_words])

        self.word_toint = {elem : i + 1 for (i, elem) in enumerate(date_words)}
        self.word_toint.update({elem : i + 2 for (i, elem) in enumerate(count_words)})
        self.word_toint.update({"one" : 1})
        self.month_toint = {elem : i + 1 for (i, elem) in enumerate(months)}

        # maybe updates is a keywords in some contextes?
        self.non_keywords = {"news", "i", "updates", "me", "you"}

        self.opinion_questions = ["what do you think about", "what's your opinion on", "what is your opinion on"]

    def to_datetime(self, date_phrase):
        now = datetime.now()
        out = now
        try:
            if date_phrase in self.special_phrases:
                date_phrase = self.translate[date_phrase]
            parts = date_phrase.split(" ")
            if date_phrase == "now":
                out = now
            elif parts[1] == "of":
                date_phrase = self.translate[date_phrase]
                parts = date_phrase.split(" ")
            elif len(parts) == 2:
                m = self.month_toint[parts[0]]
                d = self.word_toint[parts[1]]
                y = now.year
                if now.month < m or (now.month == m and now.day < d):
                    y -= 1
                try:
                    p = datetime(year=y, month=m, day=d)
                    out = p
                except ValueError:
                    out = datetime.now()
            else:
                if parts[-1] == "ago":
                    i = self.word_toint[parts[0]];
                    if parts[1] == "months":
                        parts[1] = "weeks"
                        i *= 4.3 # A month is on average 4.333... weeks.
                    call = "timedelta(" + parts[1] + "=" + str(i) + ")"
                    p = eval(call)
                    out = now - p
                elif parts[0] == "last":
                    try:
                        parts[1] = str(int(parts[1]))
                    except ValueError:
                        parts[1] = str(self.word_toint[parts[1]])
                    if parts[-1] == "months":
                        parts[-1] = "weeks"
                        parts[1] = str(int(parts[1]) * 4.3)
                    call = "timedelta(" + parts[2] + "=" + parts[1] + ")"
                    p = eval(call)
                    out = now - p
        except: # If date parsing failed (due to illegal date) use 'now'.
            # Check if datefinder can't find anything as well
            dates = list(datefinder.find_dates(np))
            if len(dates) > 0:
                return dates[0]
            return None
        return out

    # The NLP equivalent of processCommand from chatengine.py
    def process_query(self, query):
        query = query.encode('utf-8')
        # Replaced with server implementation, should be removed.
        # ptree = list(self.parser.raw_parse(query))[0]

        cmd = None
        for p in self.opinion_questions:
            idx = query.find(p)
            if idx >= 0:
                cmd = "present_opinion_subject"
                # extract the phrase subject
                args = query[idx+len(p):]
                if any(args[-1] == s for s in [".", "?", " "]):
                    args = args[:-1]
                # args should be in list form 
                args = [args.strip()]
                break

        if cmd is None:
            # Parse the sentence and make a tree from the resulting string.
            parse = self.parser.annotate(query, properties={
              'annotators': 'parse',
              'outputFormat': 'json'
              })
            ptree = Tree.fromstring(parse['sentences'][0]['parse'])

            cmd = "present_news_preferences"
            args = self.process_tree(ptree)

        return cmd, args

    # No longer necessary.
    # def process_queries(self, queries, debug=False):
    #     ptrees = self.parser.raw_parse_sents(queries)
    #     for ptree, query in zip(ptrees, queries):
    #         print("------------")
    #         print(query)
    #         self.process_tree(list(ptree)[0], debug)

    def process_tree(self, tree, debug=False):
        np_trees = self._find_NP_Leaves(tree)
#        logical_leaves = self._find_logical_leaves(tree)

        nps = [" ".join(t.leaves()).lower() for t in np_trees]
        nps = [np[4:] if np[:3] == 'the' else np for np in nps]
        if debug:
            print("NPs:", list(nps))
        # see if NPs contain places or news sources
        sources = [np for np in nps if np in self.source_ents]
        places = [np for np in nps if np in self.place_ents]
        dates = [np for np in nps if self.find_dates(np)]
        dates = [self.to_datetime(np) for np in dates]
        dates.sort()
        cats = [np for np in nps if np in self.categories]
        filters = set(sources) | set(dates) | set(places) | set(cats) # union
        nps = set(nps) - filters
#        keywords = {np for np in nps if not len(set(np.split(" ")) & self.non_keywords)}
        keywords = {np for np in nps if not set(np.split(" ")) & self.non_keywords} # no commons

        if debug:
            print("sources:", list(sources))
            print("places", list(places))
            print("dates:", list(dates))
            print("keywords:", list(keywords))
            print("categories:", list(cats))

        if not len(filters | keywords):
            return "failed_search", "I'm not sure what you mean by '%s'." % (" ".join(tree.leaves()))

        if len(dates) > 2:
            return "failed_search", "Try to use less dates in your question."
        if len(places) > 2:
            return "failed_search", "Sorry, I don't understand the region you want me to search news in."
        if len(keywords) > 2:
            return "failed_search", "I'm sorry, your question is a bit too long for me. Try searching only for '%s' and '%s'." % (keywords[0], keywords[1])
        if len(cats) > 2:
            return "failed_search", "I'm sorry, your question is a bit too long for me. Try searching only for '%s' and '%s'." % (cats[0], cats[1])
        if len(sources) > 2:
            return "failed_search", "Try specifying just one or two news sources."




        # dictionary get like operator for list
        get = lambda l, i: None if i > len(l)-1 else list(l)[i]
        # maybe create this dict dynamically?
        return [{"term1" : get(keywords, 0), "term2" : get(keywords, 1), "cat1" : get(cats, 0),
        "cat2" : get(cats, 1), "date1" : get(dates, 0), "date2" : get(dates, 1),
        "place": get(places, 0), "source1" : get(sources, 0), "source2" : get(sources, 1)}]


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

    def _find_logical_leaves(self, t):
        # If connectitive found, traverse up until NP, and then take the first NP leave of that NP
        # as an logical argument
        nleaves = len(t.leaves())

        for i in range(nleaves):
            l = t.leaf_treeposition(i)
            print(l)
            print(t[l])
            continue
            if l.parent().label() == "CC": # and/or
                # search the modified terms
                print("Yes CC!")
            elif l.parent().label() == "RB": # not
                print("Yes RB!")


if __name__ == "__main__":
    with open("testcorpus.txt", "r") as f:
#        questions = f.read().splitlines()
        questions = ["I want some news related to Donald Trump but not Bernie Sanders.", "I want some news related to Donald Trump and Bernie Sanders."]
        parser = POSParse()

        # Replaced, to be removed.
        # parser.process_queries(questions, debug=True)

        # Prints datetime objects corresponding to the date_phrases.
        # for dp in parser.date_phrases:
        #     print("--------------------")
        #     print(dp)
        #     print(parser.to_datetime(dp))

        # Parse the questions.
        for q in questions:
            print("------------")
            print(q)
            parser.process_query(q)
