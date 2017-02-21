import re
import math
import operator
from collections import Counter
from difflib import SequenceMatcher

word = re.compile(r'\w+')

class ArticleSearch(object):
    """
    Use like: relevant_articles = ArticleSearch('search term', articles).articles
    """

    def __init__(self, search_term, article_list):
        self.article_list = article_list.news
        self.search_term_vec = self.text_to_vector(search_term.lower())
        self.articles = self.search()

    def search(self):
        scored_articles = []
        for article in self.article_list:
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