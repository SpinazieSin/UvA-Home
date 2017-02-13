# -*-coding:utf-8-*-
"""Keyword extraction class for the media understanding 2017 project.

https://www.airpair.com/nlp/keyword-extraction-tutorial
    
File name: test.py
Author: Media Undertanding 2017
Date created: 7/2/2017
Date last modified: 7/2/2017
Python Version: 3.4
"""

import operator
import RAKE as r
import wordcounter as w

debug = False

class GetKeyWords():
    def __init__(self):
        # "SmartStoplist.txt" is the stopword filepath
        self.stopwords = self.get_stopwords("SmartStoplist.txt")
        self.raker = r.Rake(self.stopwords)
        self.counter = w.WordCounter(self.stopwords)

    def get(self, text):
        rake_keys = self.get_rake(text, True)
        top_keys = self.get_top(text, True)
        key_list = {}
        for rake_key in rake_keys:
            key_list[rake_key] = 0
            key_score = 0
            for top_key in top_keys:
                if top_key[0] in rake_key:
                    key_score += top_key[1]
            key_list[rake_key] = key_score
        return [x[0] for x in sorted(key_list.items(), key=operator.itemgetter(1), reverse=True)]

    def get_stopwords(self, stopword_filepath, scored=False):
        stopwords = []
        for line in open(stopword_filepath):
            if (line.strip()[0:1] != "#"):
                for word in line.split( ): #in case more than one per line
                    stopwords.append(word)
        return stopwords

    def get_rake(self, text, scored=False):
        raked_list = []
        max_raked_word_length = 60
        if scored:
            raked_result = self.raker.run(text)
            depth = int(len(raked_result)/4)
            for raked_key in raked_result[:depth]:
                if len(raked_key[0]) < max_raked_word_length:
                    raked_list.append(raked_key[0])
        else:
            raked_list = self.raker.run_noscore(text)
        return raked_list

    def get_top(self, text, scored=False):
        if scored:
            return [x for x in sorted(self.counter.get(text).items(), key=operator.itemgetter(1), reverse=1)]
        else:
            return [x[0] for x in sorted(self.counter.get(text).items(), key=operator.itemgetter(1), reverse=1)]

if debug:
    # text = "The long-string instrument is a musical instrument in which the string is of such a length that the ... One example of a long-string instrument was invented by the American composer Ellen Fullman. It is tuned in just intonation and played by"
    with open('test_article.txt', 'r') as myfile:
        text = myfile.read().replace('\n', '')
    keywords = GetKeyWords()
    # print("TEXT-------------------------------------\n")
    # print(text)
    # print("TOP WORDS--------------------------------\n")
    # keys = keywords.get_top(text)
    # print(keys)
    # print("RAKE ALGORITHM---------------------------\n")
    # keys = keywords.get_rake(text, False)
    # print(keys)
    keys = keywords.get(text)
    print("KEYS-------------------------------------\n")
    print(keys)