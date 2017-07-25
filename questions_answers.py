
from random import randint

class QA(object):
    def ask_for_name(self):
        q = ["What is your name?",
        "Can you tell me your name?",
        "Can I have your name?"]
        return q[randint(0,len(q)-1)]

    def ask_for_drink(self):
        q = ["What do you want to drink?",
        "What can I get you to drink?",
        "Is there anything you would like to drink?"]
        return q[randint(0,len(q)-1)]

    def order_drink(self, name, drink):
        q = [name + " would like a " + drink,
        name + " has ordered a " + drink]
        return q[randint(0,len(q)-1)]

    def ask_for_avaiable_drink(self):
        q = ["What drinks are avaiable?",
        "What drinks can the customers order?"]
        return q[randint(0,len(q)-1)]