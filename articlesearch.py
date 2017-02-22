import re
import math
import operator
import newsextractor
import datetime
from collections import Counter
from difflib import SequenceMatcher

word = re.compile(r'\w+')

class ArticleSearch(object):
    """
    Use like: relevant_articles = ArticleSearch('search term', articles).articles
    """

    def __init__(self, search_term, article_list, date1=None, date2=None, sources=None, place=None):
        if sources is None:
             self.sources = newsextractor.NewsExtractor().supported_news_papers
                            
        self.date1 = datetime.datetime.fromtimestamp(0) if date1 is None else date1
        self.date2 = datetime.datetime.now() if date2 is None else date2
        self.place = place
        
        self.article_list = article_list.news
        self.search_term_vec = self.text_to_vector(search_term.lower())
        self.articles = self.search()

    def search(self):
        scored_articles = []
        for article in self.article_list:

            # filters
            if not self.date1 <= article.published <= self.date2:
                continue    
            if not article.source in self.sources:
                continue
            if place is not None:            
                place_found = False
                for k in article.keywords: # search the full text maybe?
                    if self.place.substring(k.lower()):
                        place_found = True
                        break
                if not place_found:
                    break
            
            vec2 = self.text_to_vector(article.title.lower())
            highest_score = self.get_cosine(self.search_term_vec, vec2)
            for keyword in article.keywords:
                vec2 = self.text_to_vector(keyword)
                score = self.get_cosine(self.search_term_vec, vec2)
                if score > highest_score:
                    highest_score = score
            scored_articles.append([article, highest_score])
        return sorted(scored_articles, key=operator.itemgetter(1), reverse=True)

    def get_cosine(self, vec1, vec2):
        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        else:
            intersection = set(vec1.keys() & vec2.keys())
            # intersection = []
            # for key1 in vec1.keys():
            #     for key2 in vec2.keys():
            #         if self.similar(key1, key2) > 0.5:
            #             intersection.append(key2)
            numerator = sum([(vec1[x] * vec2[x]) for x in intersection])
            return float(numerator) / denominator

    def text_to_vector(self, text):
        global word
        return Counter(word.findall(text))

    def similar(self, word1, word2):
        return SequenceMatcher(None, word1, word2).ratio()
        
