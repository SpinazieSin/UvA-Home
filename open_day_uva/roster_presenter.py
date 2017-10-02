
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
        self.speech.say("Hi everyone!")

        current_time = datetime.datetime.now().strftime('%H:%M')
        self.speech.say("It is now {}".format(str(current_time)))
        event_list = self.ir.get_events_after("14:00")
        next_event = self.ir.get_next_event(event_list)
        [EVENT, TYPE, TIME] = [next_event[0], next_event[4], next_event[1]]
        sentence = "The next event is a {}, called {}, at {}".format(TYPE, EVENT, TIME)
        self.speech.say(sentence)

        while True:
            sentence = self.hearing.recognize().lower()
            print(type(sentence))
            print("Found: " + sentence)
            if self.nlp.is_greeting(sentence):
                self.speech.say("I greet you human")
            break
        print("Done")
