# -*-coding:utf-8-*-
"""Keyword extraction class for the media understanding 2017 project.

File name: test.py
Author: Media Undertanding 2017
Date created: 7/2/2017
Date last modified: 7/2/2017
Python Version: 3.4
"""

import operator
import RAKE as r
import wordcounter as w
import math
import time

class KeyWords(object):
    """
    keywords class
    """

    def __init__(self, stopword_filepath='SmartStoplist.txt'):
        """
        Init
        @param stopword_filepath Filepath for stopwordlist, can be modified
        """
        self.stopwords = self.get_stopwords(stopword_filepath)
        self.raker = r.Rake(self.stopwords)
        self.counter = w.WordCounter(self.stopwords)

    def extract(self, text, return_amount=10):
        """
        Does a combined rake and relevant word count of the given string in order
        to give some relevant keywords
        @param text Given text that will be extracted
        @param return_amount How many relevant words you want returned
        """
        rake_keys = self.extract_rake(text, False)
        top_keys = self.extract_top(text, True)
        key_list = {}
        for rake_key in rake_keys:
            key_list[rake_key[0]] = 0
            key_score = 0
            for top_key in top_keys:
                if top_key[0] in rake_key[0]:
                    key_score += top_key[1]
            key_list[rake_key[0]] = key_score + math.log(rake_key[1])
        final_keys = []
        previous_key = ['placehold_keyword', 0.0]
        for key in sorted(key_list.items(), key=operator.itemgetter(1)):
            if previous_key[1] < key[1] and previous_key[0] not in key[0] and key[0] not in previous_key[0]:
                previous_key = key
                final_keys.append(key)
        return [x[0] for x in sorted(final_keys, key=operator.itemgetter(1), reverse=True)[:return_amount]]


    def get_stopwords(self, stopword_filepath):
        """
        Creates a stopword list for both the rake and wordcounter algorithms
        @param stopword_filepath The stopwordlist that will be used
        """
        stopwords = []
        for line in open(stopword_filepath):
            if (line.strip()[0:1] != "#"):
                for word in line.split( ): #in case more than one per line
                    stopwords.append(word)
        return stopwords

    def extract_rake(self, text, scored=False):
        """
        Does a keyword extraction according to the rake algortihm
        Source: https://pdfs.semanticscholar.org/5a58/00deb6461b3d022c8465e5286908de9f8d4e.pdf
        @param text Text that will be raked
        @param scored True if you want the results to have a score
        """
        raked_list = []
        max_raked_word_length = 40
        if scored:
            raked_result = self.raker.run(text)
            depth = int(len(raked_result)/4)
            for raked_key in raked_result[:depth]:
                if len(raked_key[0]) < max_raked_word_length:
                    raked_list.append(raked_key)
        else:
            key_index = 0.0
            for raked_key in self.raker.run_noscore(text):
                key_index += 0.1
                raked_list.append([raked_key, key_index])
        return raked_list

    def extract_top(self, text, scored=False):
        """
        Extract the top 10 words that are not in the stopwordlist from a text
        @param text Text that will be extracted
        @param scored True if you want the results to have a score
        """
        if scored:
            return [x for x in sorted(self.counter.get(text).items(), key=operator.itemgetter(1), reverse=1)]
        else:
            return [x[0] for x in sorted(self.counter.get(text).items(), key=operator.itemgetter(1), reverse=1)]