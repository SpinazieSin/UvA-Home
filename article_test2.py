import articlesearch
import newsextractor
import keywords

import numpy as np# !not necessary for production!

from nltk.stem.snowball import SnowballStemmer

class Articletest(object):
    def __init__(self, articles):
        self.searcher = articlesearch.ArticleSearch(articles)
        self.keys = keywords.KeyWords()
        self.stemmer = SnowballStemmer("english")

    def get_keywords(self, article):
        return set(self.keys.extract_top(article.text.encode('utf-8')))

    def article_suggester(self, article):
        print("\n==========================================")
        print("Title: " + article.title)
        articlekeys = self.get_keywords(article)
        results = []

        # Werkt nog niet goed vanwege onderstaande;
        # keys van huidig artikel worden wel gestemt en die van target artikelen
        # niet.
        # articlekeys = {self.stemmer.stem(key) for key in articlekeys}
        for k in articlekeys:
            arts = self.searcher.search(k)
            # Check if we can find sufficient articles for this term.
            # 0 articles would give divide by 0 and 1 article would mean
            # we can only find this article rendering the term useless.
            if(len(arts) > 1):
                s = 0.
                t = len(arts) * len(articlekeys)
                for arti in self.searcher.search(k):
                    s += len(articlekeys) - len(articlekeys - self.get_keywords(arti[0]))
                results += [(k, s / t)]
            else:
                results += [(k, 0)]
        results = sorted(results, key=lambda x: x[1])[::-1]

        print("==========================================")
        print("Keywords and ranking:")
        maxlen = len(max([keypair[0] for keypair in results], key=len))
        for keypair in results:
            print("* {0:{width}} {1}".format(keypair[0], keypair[1], width=maxlen))
            # print("* " + keypair[0] + " " + str(keypair[1]))

        print("==========================================")
        top_terms = [pair[0] for pair in results if pair[1] > .1]
        if len(top_terms) < 3:
            top_terms = [pair[0] for pair in results[:3]]
        print("The relevant news query is:\n'" + " ".join(top_terms) + "'")
        print("Top 10 related news articles:")
        for art in self.searcher.search(" ".join(top_terms))[:10]:
            print("* " + art[0].title)

        return article

def main():
    # setup replica class etc
    articles = newsextractor.NewsExtractor()
    articles.build_all()
    tester = Articletest(articles)
    article_list = articles.news

    for i in np.random.randint(0, 500, 10):
        result = tester.article_suggester(article_list[i])

if __name__=="__main__":
    main()
