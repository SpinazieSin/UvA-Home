# -*-coding:utf-8-*-
"""Chat engine class file for the media understanding 2017 project.

File name: article.py
Author: Media Undertanding 2017
Date created: 7/2/2017
Date last modified: 7/2/2017
Python Version: 3.6
"""


# import other classes here, like NLP class

import posparse
import newsextractor as extract
import articlesearch
import prettynews
import os
import platform
import conversation
import profilegetter
from speechRecognition import speech as STT


class ChatEngine(object):
    """
    Base class for recieving and communicating messages between classes.

    The engine runs in a mode which determines how it will answer. Possible
    modes are human and debug. Human parses queries as natural language
    (it tries to understand them), and debug calls a function ("command")
    assigned to a specific query string. 'human_speech' is the same as human,
    but...
    """

    def __init__(self, user="", mode="human_speech", news=None):
        self.user = user
        self.mode = mode
        # get all articles
        n = news
        if n is None:
            n = extract.NewsExtractor()
            n.build_all()

        self.searcher = articlesearch.ArticleSearch(n)
        self.newsprinter = prettynews.PrettyNews(self.searcher)
        self.commands = {
            "topics": self.get_topics, "switch": self.switch, "help": self.print_commands,
            "quit": self.quit, "search": self.searcher.search,
            "present_news": self.newsprinter.show_news,
            "failed_search": self.newsprinter.search_help
        }
        self.posparser = posparse.POSParse()
        if platform.system() == 'Darwin':  # OS X
            self.speak = self.osx_speak
        else:  # Assume linux/naoqi
            import naoqiutils
            self.speak = naoqiutils.speak

    def start(self):
        conv = conversation.Conversation(self)
        if self.mode == 'human' or self.mode == 'human_speech':
            conv.start_conversation()

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
                self.speak("I assume you just want another article, don't you?")
                conv.start_conversation()
                continue
            if self.mode == 'debug':
                self.process_command(q)
            elif self.mode.startswith('human'):
                # Differentiate between IR queries and opinion related stuff
                # Something like: read me the first article/article by title/article approxiatmely
                # by title?
                cmd, args = self.posparser.process_query(q)
                if self.mode == 'human_speech':
                    self.speak(self.process_command_args(cmd, args))
                else:
                    self.process_command_args(cmd, args)


    def osx_speak(self, phrase):
        os.system("say " + phrase)

    def quit(self):
        import sys
        print("Goodbye!")
        sys.exit(0)

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

    def process_command_args(self, cmd, args):
        return self.commands.get(cmd, self.not_found)(*args)

    # This function extracts the arguments from a
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
