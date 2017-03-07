import articlesearch
import time
import pickle
import datetime
import datefinder

url_list = set()
article_list = []

with open('news.pickle', 'rb') as handle:
    x = pickle.load(handle)
handle.close()

for article in x:

#    print(type(article.published))
    if type(article.published) == type("str"):
        if article.published is None or article.published == "":
            continue
        print(article.published)
        print(list(datefinder.find_dates(article.published)))
        article.published = list(datefinder.find_dates(article.published))[0].replace(tzinfo=None)
        print(article.published)

    if article.url not in url_list:
        article_list.append(article)
        url_list.add(article.url)
        
    with open('news.pickle', 'wb') as output:
        pickle.dump(article_list, output, protocol=pickle.HIGHEST_PROTOCOL)    
        