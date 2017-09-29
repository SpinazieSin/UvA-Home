
from interaction.hearing import Hearing
from naoqi import Naoqi

class RosterPresenter:
    def __init__(self, naoqi):
        self.naoqi = naoqi
        self.hearing = Hearing(self.naoqi)

    def present(self):
        while True:
            sentence = self.hearing.recognize()
            print("Found: " + sentence)
            break
        print("Done")