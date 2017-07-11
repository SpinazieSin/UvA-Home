import articlesearch
import newsextractor
import keywords
import naoqi
import pickle
from faceRecognition import *
class Articletest(object):
	def __init__(self, articles):
		self.searcher = articlesearch.ArticleSearch(articles)
		self.keywords = keywords.KeyWords()


	def article_suggester(self, article):

		return article



def main():
	# setup replica class etc
	articles = newsextractor.NewsExtractor()
	articles.build_all()
	tester = Articletest(articles)

	article_list = []
	print(len(article_list))
	for article in articles.news:
		# temp = article
		# temp.keywords = set(article.keywords)
		# article_list.append(temp)
		print(article.keywords)
		print(tester.keywords.extract(article.text))
		print("---------------------------------")

	# with open('news1.pickle', 'wb') as handle:
	# 	pickle.dump(article_list, handle)

	# call function
	# result = tester.article_suggester(article_list[0])
	# print(result.keywords)

if __name__=="__main__":
	main()