
from interaction.hearing import Hearing
from interaction.speech import Speech
import opendag_IR
from naoqi import Naoqi
import datetime

class RosterPresenter:
    def __init__(self, naoqi):
        self.naoqi = naoqi
        self.hearing = Hearing(self.naoqi)
        self.speech = Speech(self.naoqi)

    def present(self):
        self.speech.say("Hi everyone!")

        current_time = datetime.datetime.now().strftime('%H:%M')
        self.speech.say("It is now {}".format(str(current_time)))
        eventlist = opendag_IR.get_events('./open_day_uva/opendagdata.csv')
        eventlist = opendag_IR.remove_duplicates(eventlist)
        eventlist = opendag_IR.get_events_after(eventlist, "14:00")
        next_event = opendag_IR.get_next_event(eventlist)
        EVENT = next_event[0]
        TYPE = next_event[4]
        TIME = next_event[1]
        sentence = "The next event is a {}, called {}, at {}".format(TYPE, EVENT, TIME)
        self.speech.say(sentence)

        while True:
            sentence = self.hearing.recognize()
            print("Found: " + sentence)
            break
        print("Done")
