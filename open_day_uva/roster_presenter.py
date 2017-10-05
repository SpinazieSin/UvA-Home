from interaction.hearing import Hearing
from interaction.speech import Speech
from opendag_IR import OpendagIR
from language_processing import LanguageProcessing
from naoqi import Naoqi
import datetime

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
            break
        print("Done")
