class ArticleSearch(object):
    """
    Use like: relevant_articles = ArticleSearch('search term', articles).articles
    """

    def __init__(self, search_term, article_list):
        self.search_term = search_term
        self.article_list = article_list.news
        self.articles = self.search()

    def search(self):
        search_term = self.search_term.lower()
        relevant_articles = []
        for article in self.article_list:
            if search_term in article.title.lower():
                relevant_articles.append(article)
                continue
            for keywords in article.keywords:
                if search_term in keywords.lower():
                    relevant_articles.append(article)
                    break
        return relevant_articles