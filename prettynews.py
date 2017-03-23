# -*-coding:utf-8-*-
"""Presents a list of found articles according to some criteria in a user friendly way

File name: article.py
Author: Media Undertanding 2017
Date created: 7/2/2017
Date last modified: 7/2/2017
Python Version: 3.6
"""

import articlesearch
from random import choice
import chatengine
import operator
from collections import Counter

class PrettyNews(object):
    
    def __init__(self, searcher, mode, chat):
        self.searcher = searcher
        self.mode = mode
        self.NOTHING_FOUND = ["I could not find any articles for you.", "I'm afraid I can't do that."]
        self.chat = chat
        
    # Extract a few articles for presentation according to some parameters
    def filter_news(self, filters, items=5, score_thresh=0.5):
        articles = self.searcher.search(**filters)[:items]           
        articles = [a for a in articles if a[1] > score_thresh]
        articles.sort(key=operator.itemgetter(1), reverse=True)
        return [a[0] for a in articles]

    def show_news(self, filters, items=5, score_thresh=0.5):
        try:
            articles = self.filter_news(filters, items=items, score_thresh=0.5)
        except:
            return "speak", [choice(["I'm not sure what you mean.", "I'm afraid I can't help you with that.", "Sorry, I didn't catch that?", "I'm sorry %s, I'm afraid I can't do that" % (self.chat.user.username)])]
        if not len(articles):
            phrase = choice(self.NOTHING_FOUND)
#            print(phrase)
            return "speak",  [fail_phrase]
        longest_name = len(max(articles, key=lambda a: len(a.title)).title)
        phrase = "I found the following articles for you: "
        for a in articles:
            print('{0: <{width}} - {1}'.format(a.title.encode('utf-8'), a.url, width=longest_name))
            phrase += "'%s', " % (a.title)
        self.chat.speak(phrase[:-2] + ".")
        return "ir_answer", [articles]
        
    def show_news_preferences(self, filters, score_thresh=0.5):
        user = self.chat.user
        fave_categories = {c for c, i in user.interests.iteritems() if i > 0.6}
        articles = self.filter_news(filters, items=None, score_thresh=0.5) # l[None:None] == l[:]
        if not len(articles):
            fail_phrase = choice(self.NOTHING_FOUND)
            return "speak", [fail_phrase]
        # further filter articles according to preferences
        prefered_articles = []
        interest_counter = Counter(articles)

        for a in articles:
            for keyword in a.keywords:
                if keyword in user.keywords:
                    interest_counter[a] += 1
            if a.category in fave_categories:
                interest_counter[a] += 1
                
        fave_articles = interest_counter.most_common(3)
        
        if len(fave_articles) == 1 or fave_articles[0][1] > fave_articles[1][1]:
            a = fave_articles[0][0]
            prefered_articles.append(a)
            phrase = "Do you want me to read: '%s'?" % (a.title)
        elif len(fave_articles) == 2 or fave_articles[1][1] > fave_articles[2][1]:
            a1 = fave_articles[0][0]
            prefered_articles.append(a1)
            a2 = fave_articles[0][0]
            prefered_articles.append(a2)
            phrase = "Are you interested in '%s' or in '%s'?" % (a1.title, a2.title)
        else: # all equal
            phrase = "I found the following articles for you:\n"
            for a in fave_articles:
                prefered_articles.append(a[0])
                phrase += "'%s'\n" % (a[0].title)
            phrase += "Do you want me to read any of them?"

        self.chat.speak(phrase)
        return "ir_answer", [prefered_articles]


    def search_help(self, reason):
        phrase = "I can not do that for you. " + str(reason)
        return "speak", [phrase]






