# -*-coding:utf-8-*-
from random import choice, randrange, randint, random
from collections import deque, Counter
import newsextractor as extract
import collections
import articlesearch
import re
import posparse
import operator
from nltk.stem.snowball import SnowballStemmer
import unicodedata
from nltk.tree import *
import article
import subprocess
import articlesearch
import keywords

class Conversation(object):

    def __init__(self, chat, art_history=8, news=None):
        self.chat = chat
        self.article_context = collections.deque([None]*art_history, maxlen=art_history)
        self.context = [] # more general context
        # get all articles
        n = news
        self.AFFIRMATIVE = ["Okay.", "Good.", "Sure.", "That's cool bro."]
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
            arts = self.searcher.search(cat1=cat)
            arts = {a[0] for a in arts if usr_keys & set(a[0].keywords)}
            if not len(arts):
                tries -= 1
                continue
            # add article to context
            self.article_context.appendleft(list(arts)[0])
            phrase = "I found an article on '%s' for you. Pretty cool right?" % (list(arts)[0].title)
            break
        if not tries:
            phrase = "What kind of news do you want to talk about today?"

#        if self.chat.mode == "human_speech":
#            self.chat.speak(phrase)
#        print(phrase)
        return phrase

    def read(self, article):
        lines = article.text.split(".") # maybe split on sentence markers.
        preference_chance = 0.3
        opinion_chance = 1
        start_end = 4
        if len(lines) < start_end:
            self.chat.speak("Okay, I will read you '%s'. %s" % (article.title, lines))
            # either present an opinion or ask the user about preferences
            if randrange(0,2):
                if randrange(0,1) < preference_chance:
                    return "get_preference", [article]
            else:
                if randrange(0,1) < opinion_chance:
                    return "present_opinion_article", [article]
            return None, [None]
        else:
            start_lines = randint(2, start_end)

        first_lines = lines[:start_lines]
        second_end = randint(start_lines, ((len(lines)-start_lines)//2)+3)
        second_part = ".".join(lines[start_lines:second_end])
        third_part = ".".join(lines[second_end:])
        self.chat.speak("Okay, I will read you '%s'. %s" % (article.title, ".".join(first_lines)))
        self.chat.speak("Do you want me to continue reading?")
        q = self.chat.listen()
        self.chat.speak(choice(self.AFFIRMATIVE))

        if "yes" in q:
            self.chat.speak(second_part)
        if "no" in q:
            if randrange(0,2):
                if randrange(0,1) < preference_chance:
                    return "get_preference", [article]
            else:
                if randrange(0,1) < opinion_chance:
                    return "present_opinion_article", [article]
            return None, [None]

        self.chat.speak("Do you want me to continue reading?")
        q = self.chat.listen()
        self.chat.speak(choice(self.AFFIRMATIVE))
        if "yes" in q:
            self.chat.speak(third_part)
            if randrange(0,2):
                if randrange(0,1) < preference_chance:
                    return "get_preference", [article]
            else:
                if randrange(0,1) < opinion_chance:
                    return "present_opinion_article", [article]
        return None, [None]

    def read_text(self, text):
        lines = text.split(".")  # maybe split on sentence markers.
        preference_chance = 0.35
        opinion_chance = 0.5
        start_end = 6
        if len(lines) < start_end:
            self.chat.speak("%s" % (lines))
            return None, [None]
        else:
            start_lines = randint(2, start_end)

        first_lines = lines[:start_lines]
        second_end = randint(start_lines, ((len(lines)-start_lines)//2)+3)
        second_part = ".".join(lines[start_lines:second_end])
        third_part = ".".join(lines[second_end:])
        self.chat.speak("%s" % (".".join(first_lines)))
        self.chat.speak("Do you want me to continue reading?")
        q = self.chat.listen()
        self.chat.speak(choice(self.AFFIRMATIVE))

        if "yes" in q:
            self.chat.speak(second_part)
        if "no" in q:
            return None, [None]

        self.chat.speak("Do you want me to continue reading?")
        q = self.chat.listen()
        self.chat.speak(choice(self.AFFIRMATIVE))
        if "yes" in q:
            self.chat.speak(third_part)
        return None, [None]

    def get_preference(self, article):
        self.chat.speak("What did you think about %s?" % (article.title))
        q = self.chat.listen()
        sentiment_command = "java -jar ./SentiStrengthCom.jar sentidata ./SentiStrengthData/ text \"" + q + "\""
        proc = subprocess.Popen(sentiment_command, stdout=subprocess.PIPE, shell=True)
        sentiment = proc.stdout.read().strip().split(" ")
        try: 
            pos_sent = int(sentiment[0])
            neg_sent = int(sentiment[1])
            
        except:
            self.chat.speak("I am not sure what you meant with that.")
            return "get_preference", [article]

        # Do sentiment analysis with sentistrength (as much negative as postive is negative)
        if abs(neg_sent) > (pos_sent + 1):
            self.chat.speak("I'm sorry to hear that.")
            return "update_preference", [neg_sent, article]
        elif pos_sent > (abs(neg_sent) + 1):
            self.chat.speak("I'm glad you liked it.")
            return "update_preference", [pos_sent, article]
        else:
            return "speak", ["Okay, that's fine."]




    # Parse the answer to a news retrieval query
    # context is a list of previously read articles
    def ir_parse(self, articles, tries=3):

        art_ref = {("first", "1st", "1", "one") : 0, ("second", "2nd", "2") : 1, ("third", "3rd", "3", "last") : 2}
        self.article_context.extendleft(articles)

        titles = [a.title.lower() for a in articles]
        article = None

        while tries and article is None:
            q = self.chat.listen()
            if any(a in q for a in ["yes", "y", "yeah"]):
                article = articles[0]
            elif "no" in q:
                return None, [None]

            article_idx = self.article_by_title(q, titles)
            if article_idx:
                article = articles[article_idx]
            for r_tuple, v in art_ref.iteritems():
                if any(r in q for r in r_tuple):
                    article = articles[v]

            if article is not None: # found
                break
            else:
                self.chat.speak("Please refer to the article you want me to read.")
                tries -= 1

        if tries == 0:
            return "speak", ["Oops! Didn't quite get you there."]

        return "read_article", [article] # Read article should sometimes randomly asks a users opinion
                                       # to construct preferences

    def remove_non_ascii(self, string):
        new_string = ''.join([i if ord(i) < 128 else ' ' for i in string])
        return str(new_string)

    # returns index of article that should be read
    def article_by_title(self, q, titles):
        posparser = posparse.POSParse()
        important_constituents = ['NN', 'NNP', 'N']
        stemmed_titles = [Counter() for _ in range(len(titles))]
        word = re.compile(r'\w+')
        title_vecs = [word.findall(t) for t in titles]
        stemmer = SnowballStemmer("english")

        for idx, t in enumerate(title_vecs):
            for w in t:
                stem = stemmer.stem(w)
                if len(stem) > 1:
                    stemmed_titles[idx][stem] += 1
                else:
                    stemmed_titles[idx][w] += 1

        question_vec = word.findall(q)
        stemmed_question = Counter()
        for w in question_vec:
            stem = stemmer.stem(w)
            if len(stem) > 1:
                stemmed_question[stem] += 1
            else:
                stemmed_question[w] += 1

        for idx, t in enumerate(titles):
            parse = posparser.parser.annotate(self.remove_non_ascii(t), properties={
            'annotators' : 'parse',
            'outputFormat' : 'json'
            })

            ptree = Tree.fromstring(parse['sentences'][0]['parse'])
            for w_tuple in ptree.pos():
                # some words are more important
                if w_tuple[1] in important_constituents:
                    stem = stemmer.stem(w_tuple[0])
                    if len(stem) > 1:
                        stemmed_titles[idx][stem] += 1
                    else:
                        stemmed_titles[idx][w] += 1

        parse = posparser.parser.annotate(q, properties={
        'annotators': 'parse',
        'outputFormat': 'json'
        })
        ptree = Tree.fromstring(parse['sentences'][0]['parse'])
        for w_tuple in ptree.pos():
            # some words are more important
            if w_tuple[1] in important_constituents:
                stem = stemmer.stem(w_tuple[0])
                if len(stem) > 1:
                    stemmed_question[stem] += 1
                else:
                    stemmed_question[w] += 1

        scores = [self.searcher.similar(stemmed_question, t) for t in stemmed_titles]
        score_idx, max_score = max(enumerate(scores), key=operator.itemgetter(1))
        if max_score > 0.15:
            scores = [float(s)/float(max_score) for s in scores]
            return score_idx
        else:
            return None

    def related_news_parse(self, query, article): # Wijnands thingy
        if self.chat.mode == "human_speech":
            self.chat.speak(phrase)



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
    # Needs a chat
    conv = Conversation()
    conv.article_by_title("Show me the trump one.", ['On Comedy: Why Do Comics Laugh at Their Own Jokes? It’s No Accident', 'In Israel, Lauding and Lamenting the Era of Trump', "Carson calls slaves 'immigrants' in speech, drawing criticism"])
