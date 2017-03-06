# -*-coding:utf-8-*-

from random import choice

class Conversation(object):
    
    def __init__(self, chat):
        self.chat = chat
        print("🚫 This class uses an unneeded set conversion on line 23")

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
            arts = {a[0] for a in arts if usr_keys & set(a[0].keywords)}
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

    # The rest of this class will contain other conversational keypoints/modes
    
    def end_conversation():
        return "Goodbye?"