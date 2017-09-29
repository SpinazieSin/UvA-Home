
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
        eventlist = opendag_IR.get_events()
        eventlist = opendag_IR.remove_duplicates(eventlist)
        eventlist = opendag_IR.get_events_subject("chemistry", eventlist)
        EVENT = eventlist[0][0]
        TIME = eventlist[0][1]
        sentence = "The next event is {} at {}".format(EVENT, TIME)
        while True:
            sentence = self.hearing.recognize()
            print("Found: " + sentence)
            break
        print("Done")
