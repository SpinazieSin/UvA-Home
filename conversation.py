# -*-coding:utf-8-*-

from random import choice
from collections import deque
import newsextractor as extract
import articlesearch
import keywords

class Conversation(object):

    def __init__(self, chat, news=None):
        self.chat = chat
        self.newscontext = deque()  # stack of the news
        self.newscontext = []  # more general context
        # get all articles
        n = news
        if n is None:
            n = extract.NewsExtractor()
            n.build_all()

        self.keywords = keywords.KeyWords()
        self.searcher = articlesearch.ArticleSearch(n)

    # A little introduction to the conversation
    def start_conversation(self):
        found_artile = False
        tries = 2050
        interest_thresh = 0.5
        relevance_thresh = 0.1
        user_interest = [k for k,v in self.chat.user.interests.items() if v > interest_thresh]
        usr_keys = set(self.chat.user.keywords)
        while tries:
            cat = choice(user_interest)
            arts = self.chat.searcher.search(cat1=cat)
#            print([set(a[0].keywords) for a in arts])
            arts = {a[0] for a in arts if usr_keys & a[0].keywords}
            if not len(arts):
                tries -= 1
                continue
            phrase = "I found an article on '%s' for you. Pretty cool right?" % (list(arts)[0].title)
            break

        if not tries:
            phrase = "What kind of news do you want to talk about today?"

        if self.chat.mode == "human_speech":
            self.chat.speak(phrase)

        print(phrase)


    def related_news_parse(self, article): # Wijnands thingy
        article.keywords # lange keywords
        keys.extract_top(article.text, True) # most frequent keywords
        pass

    def query_parse(self, query):
        # add to context
        # do a posparse
        # Do you want me to read 'title' etc.
        pass

    # Talk about query results/await the information retrievel answer
    # So yes/no to questions about the query
    def ir_answer(self, answer):
        pass

    # The rest of this class will contain other conversational keypoints/modes

    def end_conversation(self):
        return "Goodbye?"

if __name__ == "__main__":
    with open("testcorpus.txt", "r") as f:
        questions = f.read().splitlines()
        parser = POSParse()
        # parser.process_queries(questions, debug=True)
        # for dp in parser.date_phrases:
        #     print("--------------------")
        #     print(dp)
        #     print(parser.to_datetime(dp))

        for q in questions:
            print("------------")
            print(q)
            parser.process_query(q)
