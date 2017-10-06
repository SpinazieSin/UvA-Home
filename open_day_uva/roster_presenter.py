
from interaction.hearing import Hearing
from interaction.speech import Speech
from opendag_IR import OpendagIR
from language_processing import LanguageProcessing
from naoqi import Naoqi
import time
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

        break_count = 0
        while True:
            sentence = self.hearing.recognize().lower()
            print("Sentence: " + sentence)
            answer = self.nlp.get_command(sentence)
            broke_up_answer = answer.split(",")
            for part_answer in broke_up_answer:
                self.speech.say(answer)
                time.sleep(0.5)

            if break_count > 5:
                break
            break_count += 1
        print("Done")
