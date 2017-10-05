
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
            sentence = self.hearing.recognize().lower()
            print("Sentence: " + sentence)
            answer = self.nlp.get_command(sentence)
            self.speech.say(answer)
            break
        print("Done")
