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

    def show_news(self, filters, items=5, print_sources=False):
        # first search for the news
        articles = self.searcher.search(**filters)[:items]
        articles = {a[0] for a in articles}
        longest_name = len(max(articles, key=lambda a: len(a.title)).title)
        for a in articles:
            print('{0: <{width}} - {1}'.format(a.title, a.url, width=longest_name))

        
