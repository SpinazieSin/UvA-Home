# -*-coding:utf-8-*-
"""Presents a list of found articles according to some criteria in a user friendly way

File name: article.py
Author: Media Undertanding 2017
Date created: 7/2/2017
Date last modified: 7/2/2017
Python Version: 3.6
"""

import articlesearch

class PrettyNews(object):
    
    def __init__(self, searcher):
        self.searcher = searcher

    def show_news(self, filters, items=5, print_sources=False, score_thresh=0.2):
        # first search for the news
        articles = self.searcher.search(**filters)[:items]
        articles = {a[0] for a in articles if a[1] > score_thresh}
        if not len(articles):
            print("I could not find any articles for you.")
            return
        longest_name = len(max(articles, key=lambda a: len(a.title)).title)
        phrase = "I found the following articles for you: "
        for a in articles:
            print('{0: <{width}} - {1}'.format(a.title.encode('utf-8'), a.url, width=longest_name))
            phrase = "'%s', " % (a.title) 
        return phrase[:-2] + "."

    def search_help(self, reason):
        phrase = "I can not do that for you. " + str(reason)
        print(phrase)
        return phrase