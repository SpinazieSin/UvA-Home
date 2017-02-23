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

class ChatEngine(object):
    """
    Base class for recieving and communicating messages between classes.

    The engine runs in a mode which determines how it will answer. Possible
    modes are human and debug. Human parses queries as natural language
    (it tries to understand them), and debug calls a function ("command")
    assigned to a specific query string
    """

    def __init__(self, user="", mode="human"):
        self.user = user
        self.mode = mode
        # get all articles
        n = extract.NewsExtractor()
        n.build_all()
        self.searcher = articlesearch.ArticleSearch(n)
        self.newsprinter = prettynews.PrettyNews(self.searcher)
        self.commands = {
            "topics" : self.get_topics, "switch" : self.switch, "help" : self.print_commands,
            "quit" : self.quit, "search" : self.searcher.search,
            "present_news" : self.newsprinter.show_news
        }
        self.posparser = posparse.POSParse()

    def start(self):
        while True:
            q = input("> ")
            if self.mode == 'debug':
                self.process_command(q)
            elif self.mode == 'human':
                cmd, args = self.posparser.process_query(q)
                self.process_command_args(cmd, args)

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
        cmd, *args = cmd
        self.commands.get(cmd, self.not_found)(*args)
        


if __name__ == "__main__":
    c = ChatEngine()
    c.start()
