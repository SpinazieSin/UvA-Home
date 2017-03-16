# -*-coding:utf-8-*-
"""Chat engine class file for the media understanding 2017 project.

File name: article.py
Author: Media Undertanding 2017
Date created: 7/2/2017
Date last modified: 7/2/2017
Python Version: 3.6
"""

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

#... import sklearn stuff...

# import other classes here, like NLP class

import posparse
import articlesearch
import prettynews
import userprofile
import os
import platform
import conversation
import profilegetter
<<<<<<< HEAD
import userprofile
=======
from speechRecognition import speech as STT

>>>>>>> 8483fcd13c9c40a0137da425885eb383c8cb2cb5

class ChatEngine(object):
    """
    Base class for recieving and communicating messages between classes.

    The engine runs in a mode which determines how it will answer. Possible
    modes are human and debug. Human parses queries as natural language
    (it tries to understand them), and debug calls a function ("command")
    assigned to a specific query string. 'human_speech' is the same as human,
    but...
    """

    def __init__(self, user=None, mode="human", news=None):
        if not user:
            self.user = userprofile.UserProfile()
        else:
            self.user = user
        
        self.mode = mode
        self.conv = conversation.Conversation(self, news=news)
        if platform.system() == 'Darwin': # OS X
            self.say = self.osx_say
        else: # Assume linux/naoqi
            import naoqiutils
            self.say = naoqiutils.speak

        self.newsprinter = prettynews.PrettyNews(self.conv.searcher, self.mode, self)
        # Commands is a dict of named conversation action scripts
        self.commands = {
<<<<<<< HEAD
            "help" : self.print_commands,
            "quit" : self.quit,
            "present_news" : self.newsprinter.show_news,
            "present_news_preferences" : self.newsprinter.show_news_preferences,
            "failed_search" : self.newsprinter.search_help,
            "speak" : self.speak,
            "ir_answer" : self.conv.ir_parse,
            "read_article" : self.conv.read,
            "update_preference" : self.user.update_preferences,
            "get_preference" : self.conv.get_preference,
        }
        debug_commands = {
            "topics" : self.get_topics, "switch" : self.switch, 
            "quit" : self.quit,
=======
            "topics": self.get_topics, "switch": self.switch, "help": self.print_commands,
            "quit": self.quit, "search": self.searcher.search,
            "present_news": self.newsprinter.show_news,
            "failed_search": self.newsprinter.search_help
>>>>>>> 8483fcd13c9c40a0137da425885eb383c8cb2cb5
        }
        
        if mode == "debug":
            self.commands = dict(self.commands.items() + debug_commands.items())
        self.posparser = posparse.POSParse()
<<<<<<< HEAD


    def start(self):
        
        if self.mode=='human' or self.mode=='human_speech':
            cmd, args = self.conv.start_conversation()
            self.process_command_args(cmd, args)
            
        cmd = None        
=======
        if platform.system() == 'Darwin':  # OS X
            self.speak = self.osx_speak
        else:  # Assume linux/naoqi
            import naoqiutils
            self.speak = naoqiutils.speak

    def start(self):
        conv = conversation.Conversation(self)
        if self.mode == 'human' or self.mode == 'human_speech':
            conv.start_conversation()
>>>>>>> 8483fcd13c9c40a0137da425885eb383c8cb2cb5

        while True:

            # q = raw_input("> ")
            q = STT.wait_for_voice()
            if q == "":
                self.speak("Sorry I didn't hear that can you say it again?")
                q = STT.wait_for_voice()
            if q == "":
                self.speak("One More time please.")
                q = STT.wait_for_voice()
            if q == "":
                self.speak("I assume you just want another article, don't you? Here is something.")
                # currently if no question is found after 3 tries, random news
                # is requested.
                q = "can you get me the latest news"
            if self.mode == 'debug':
                self.process_command(q)
            elif self.mode.startswith('human'):
                # Differentiate between IR queries and opinion related stuff
                # Something like: read me the first article/article by title/article approxiatmely
<<<<<<< HEAD
                # by title? 
                # ^ This should go into (pos)parsing! cus that class is concerned with unnderstanding
                # sentences. It could/should go into the process_query() method
                cmd, args = self.posparser.process_query(q)
                while cmd is not None:
                    cmd, args = self.process_command_args(cmd, args)
                    
        conv.end_conversation()

    
    def speak(self, phrase):
        if self.mode == "human_speech":
            print(phrase)
            self.say(phrase.replace('"', '\"'))
        elif self.mode == "human":
            print(phrase)
        return None, None

    
=======
                # by title?
                cmd, args = self.posparser.process_query(q)
                if self.mode == 'human_speech':
                    answer = self.process_command_args(cmd, args)
                    if answer is None:
                        self.speak("I don't understand what you just said. Can you say it again.")
                    else:
                        self.speak(answer)
                else:
                    self.process_command_args(cmd, args)


    def osx_speak(self, phrase):
        os.system("say " + phrase)

>>>>>>> 8483fcd13c9c40a0137da425885eb383c8cb2cb5
    def quit(self):
        import sys
        print("Goodbye!")
        sys.exit(0)
        
    def select_random_command(self):
        pass

    def print_commands(self):
        for cmd in self.commands:
            print(cmd)

    # switch answering mode
    def switch(self, mode):
        self.mode = mode

    # dummy method
    def get_topics(self):
        print("Binnenland\nBuitenland\nOorlog")

    def not_found(self, *args):
        print("Command not found!")
<<<<<<< HEAD
        
    def osx_say(self, phrase):
        os.system("say \"" + phrase.encode('utf-8') + "\"")

        
    def process_command_args(self, cmd, *args):
        return self.commands.get(cmd, self.not_found)(*args)


        
    # This function extracts the arguments from a 
=======

    def process_command_args(self, cmd, args):
        return self.commands.get(cmd, self.not_found)(*args)

    # This function extracts the arguments from a
>>>>>>> 8483fcd13c9c40a0137da425885eb383c8cb2cb5
    def process_command(self, cmd):
        # TODO capability to do gdb like command synonyms
        cmd = cmd.lower().split(" ")
        # split the list in first and rest
        cmd = cmd[0]
        if len(cmd) > 1:
            args = cmd[1:]
        else:
            args = []
        # cmd, *args = cmd # rip beatiful python3 syntax
        self.commands.get(cmd, self.not_found)(*args)



if __name__ == "__main__":
    getter = profilegetter.ProfileGetter([])
    user = getter.get_profile("Jonathon-Gorbscheid")
    c = ChatEngine(user=user)
    c.start()
