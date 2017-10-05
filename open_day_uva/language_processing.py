
from opendag_IR import OpendagIR

class LanguageProcessing:
    def __init__(self):
        # For local testing use - self.ir = OpendagIR("opendagdata.csv")
        self.ir = OpendagIR()

    def is_break(self, q):
        if (("stop" in q or "sleep" in q or "break") and ("another" in q or "a bit" in q or "now" in q or "a while" in q or "a second" in q or "me" in q or "i want" in q or "talking" in q)) or ("shut up" in q):
            return True
        return False

    def is_quit(self, q):
        if (("stop" in q or "quit" in q or "done" in q) and "conv" in q) or q == "stop" or q == "quit":
            return True

    def is_greeting(self, q):
        if ("hello" in q or "greeting" in q or "hi" in q or "nice to" in q) and ("mikey" in q):
            return True


    def is_goodbye(self, q):
        if ("bye" in q or "goodbye" in q) and ("mikey" in q):
            return True
    def whats_your_name(self, q):
        if ("name" in q and "what" in q) or ("who" in q and "are" in q):
            return True

    # Analyzes a sentence to extract some kind of instruction
    def get_command(self, q):
        word_list = q.split(" ")
        event_list = []
        for word in word_list:
            events = self.ir.get_events_subject(word)
            if events:
                event_list.append(events)
        command = event_list
        if self.is_greeting(q):
            command = ["greeting", None]
        elif self.is_goodbye(q):
            command = ["goodbye", None]
        elif "when" in word_list:
            command = ["when", event_list]
        elif self.whats_your_name(q):
            command = ["robot_name", None]
        return command


    def next_event_sentence(self):
        current_time = datetime.datetime.now().strftime('%H:%M')
        self.speech.say("It is now {}".format(str(current_time)))
        event_list = self.ir.get_events_after("14:00")
        next_event = self.ir.get_next_event(event_list)
        [EVENT, TYPE, TIME] = [next_event[0], next_event[4], next_event[1]]
        sentence = "The next event is a {}, called {}, at {}".format(TYPE, EVENT, TIME)
        return sentence

if __name__ == "__main__":
    nlp = LanguageProcessing()
    command = nlp.get_command("hello is beth")
    print(command)
