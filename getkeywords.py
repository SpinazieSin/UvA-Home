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
        rake_keys = self.get_rake(text)
        top_keys = self.get_top(text)
        key_list = []
        for top_key in top_keys:
            for rake_key in rake_keys:
                if top_key in rake_key and rake_key not in key_list:
                    key_list.append(rake_key)
        return key_list

    def get_stopwords(self, stopword_filepath):
        stopwords = []
        for line in open(stopword_filepath):
            if (line.strip()[0:1] != "#"):
                for word in line.split( ): #in case more than one per line
                    stopwords.append(word)
        return stopwords

    def get_rake(self, text):
        raked_list = []
        max_raked_word_length = 80
        search_depth = 20
        raked_result = self.raker.run(text)
        for raked_key in raked_result[:search_depth]:
            if len(raked_key[0]) < max_raked_word_length: 
                raked_list.append(raked_key[0])
        return raked_list

    def get_top(self, text):
        return [x[0] for x in sorted(self.counter.get(text).items(), key=operator.itemgetter(1), reverse=1)]

if debug:
    # text = "The long-string instrument is a musical instrument in which the string is of such a length that the ... One example of a long-string instrument was invented by the American composer Ellen Fullman. It is tuned in just intonation and played by"
    with open('test_article.txt', 'r') as myfile:
        text = myfile.read().replace('\n', '')
    keywords = GetKeyWords()
    keys = keywords.get(text)
    print(keys)
    print("-------------------------------------------")
    # print(keys.top_keys)