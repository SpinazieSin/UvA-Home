from interaction.hearing import Hearing
from interaction.speech import Speech
from opendag_IR import OpendagIR
from language_processing import LanguageProcessing
from naoqi import Naoqi
import datetime
from random import randint

class RosterPresenter:
    def __init__(self, naoqi):
        self.naoqi = naoqi
        self.hearing = Hearing(self.naoqi)
        self.speech = Speech(self.naoqi)
        self.ir = OpendagIR()
        self.nlp = LanguageProcessing()

    def present(self):
        self.speech.say("Hi!")

        while True:
            sentence = str(self.hearing.recognize()).lower()
            print("Sentence: " + sentence)
            command = self.nlp.get_command(sentence)
            if command:
                if command[0] == "greeting":
                    self.speech.say("Greetings human!")

                elif command[0] == "break":
                    self.speech.say("I won't be listening for a vew seconds")
                elif command[0] == "robot_name":
                    self.speech.say("My name is Mickey")
                elif command[0] == "goodbye":
                    q = ["Goodbye and enjoy your day!", "See you later!", "Goodbye", "Later, sucker!", "I feel a bit shitty now that you're leaving!"]
                    answer = q[randint(0,len(q)-1)]
                    self.speech.say(answer)
            break
        print("Done")
