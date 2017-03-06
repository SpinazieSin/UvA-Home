from random import choice

class Conversation(object):
    
    def __init__(self, chat):
        self.chat = chat
        pass

    # A little introduction to the conversation
    def start_conversation(self):
        found_artile = False
        tries = 25
        interest_thresh = 0.5
        relevance_thresh = 0.3
        user_interest = [k for k,v in self.chat.user.interests if v > interest_thresh]
        while (not found_artile) and tries:
            cat = choice(user_interest)
            term = chocie(chat.user.keywords)
            arts = self.chat.searcher.search(term=term, cat1=cat)
            arts = {a[0] for a in arts if a[1] > relevance_thresh}
            if not len(arts):
                tries -= 1
                continue
            found_article = True
            phrase = "I found an article on '%s' for you. Pretty cool right?" % (arts[0].title) 

        if not tries:
            phrase = "What kind of news do you want to talk about today?"
            
        if chat.mode == "human_speech":
            self.chat.speak(phrase)

        print(phrase)

    # The rest of this class will contain other conversational keypoints/modes
    
    def end_conversation():
        return "Goodbye?"