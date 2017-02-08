# -*-coding:utf-8-*-
"""Chat engine class file for the media understanding 2017 project.

File name: article.py
Author: Media Undertanding 2017
Date created: 7/2/2017
Date last modified: 7/2/2017
Python Version: 3.6
"""


# import other classes here, like NLP class

class ChatEngine():
    """
    Base class for recieving and communicating messages between classes
    
    The engine runs in a mode which determines how it will answer. Possible modes are human and 
    debug. Human parses queries as natural language (it tries to understand them), and debug calls a 
    function ("command") assigned to a specific query string
    """
    def __init__(self, user="", mode="debug"):
        self.user = user
        self.mode = mode
        self.commands = {
            "topics" : self.get_topics, "switch" : self.switch, "help" : self.print_commands, 
            "quit" : self.quit
         }
            
    def start(self):
        while True:
            q = input("> ")
            if self.mode == 'debug':
                self.process_command(q)
            elif self.mode == 'human':
                self.process_query(q)

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

    def not_found(self):
        print("Command not found!")

    # When NLP is done, this will be replaced by a NLP function
    def process_command(self, cmd):
        # TODO capability to do gdb like command synonyms
        cmd = cmd.lower().split(" ")
        # split the list in first and rest
        cmd, *args = cmd
        self.commands.get(cmd, self.not_found)(*args)
    
    # The NLP equivalent of processCommand
    def process_query(self, query):
        2

if __name__ == "__main__":
    c = ChatEngine()
    c.start()

