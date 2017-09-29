
from interaction.hearing import Hearing
from interaction.speech import Speech
import opendag_IR
from naoqi import Naoqi

class RosterPresenter:
    def __init__(self, naoqi):
        self.naoqi = naoqi
        self.hearing = Hearing(self.naoqi)
        self.speech = Speech(self.naoqi)

    def present(self):
        self.speech.say("Hi everyone!")
        # the next event is
        while True:
            sentence = self.hearing.recognize()
            print("Found: " + sentence)
            break
        print("Done")
