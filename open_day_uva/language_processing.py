
from opendag_IR import OpendagIR
from random import randint
from sets import Set
import datetime

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
        return False

    def is_greeting(self, q):
        if ("hello" in q or "greeting" in q or "hi" in q or "nice to" in q) and ("ginger" in q or "pepper" in q or "robot" in q):
            return True
        elif ("hello" == q or "hi" == q or "nice to meet you" == q):
            return True
        return False

    def is_goodbye(self, q):
        if ("bye" in q or "goodbye" in q):
            return True
        return False

    def whats_your_name(self, q):
        if ("called" in q and "what" in q) or ("who" in q and "are" in q) or ("you" in q and "name" in q):
            return True
        return False

    def how_are_you(self, q):
        if ("how" in q and "are" in q and "you" in q):
            return True
        return False

    def good_ginger(self, q):
        if "good ginger" == q:
            return True
        return False

    def when_next_event(self, q):
        if ("next" in q and "when" in q) or ("what" in q and "coming up" in q) or ("what" in q and "is" in q and "next" in q) or ("happening" in q and "next" in q):
            return True
        return False

    def when_ongoing_event(self, q):
        if ("what" in q or "is" in q) and ("ongoing" in q or "going on" in q) or ("happening" in q and "now" in q):
            return True
        return False

    def age_requirement(self, q):
        if ("child" in q or "kids" in q) or ("year" in q or "age" in q or "old" in q):
            return True
        return False

    # Analyzes a sentence to extract some kind of instruction
    def get_command(self, q):
        word_list = q.split(" ")
        event_list = self.get_events(word_list)
        if self.is_greeting(q):
            answers = ["Greetings human!", "Hi there!", "Hi!", "Nice to meet you!"]
        elif self.how_are_you(q):
            answers = ["I am new but I am doing my best!", "I am fine thank you!", "I am Good!"]
        elif self.is_goodbye(q):
            answers = ["Goodbye and enjoy your day!", "See you later!", "Goodbye!", "Later, sucker!", "Please do not leave me here with all these people!", "Cheers mate!", "Please do not go!"]
        elif self.whats_your_name(q):
            answers = ["My name is Ginger", "I am Ginger", "Hello, I am Ginger"]
        elif self.good_ginger(q):
            answers = ["Is this Arnoud?"]
        elif self.when_next_event(q):
            answers = self.formulate_next_event(word_list)
        elif self.when_ongoing_event(q):
            answers = self.formulate_ongoing_event(word_list)
        elif self.age_requirement(q) and event_list:
            answers = self.formulate_age_requirement(event_list)
        else:
            answers = ["Error, I do not understand", "I am sorry but I do not understand you"]
        return answers[randint(0,len(answers)-1)]


    def formulate_next_event(self, word_list):
        event_list = self.get_events(word_list, True)
        current_time = datetime.datetime.now().strftime('%H:%M')
        current_time = "15:00"
        next_event_list = self.ir.get_events_after(current_time, event_list)
        if next_event_list:
            return self.specific_next_event_sentence(next_event_list)
        elif event_list:
            return ["There is no events related to that subject after {}".format(current_time)]
        else:
            return self.next_event_sentence()

    def formulate_ongoing_event(self, word_list):
        event_list = self.get_events(word_list, True)
        current_time = datetime.datetime.now().strftime('%H:%M')
        current_time = "15:00"
        next_event_list = self.ir.get_ongoing_events(current_time, event_list)
        if next_event_list:
            return self.specific_ongoing_event(next_event_list)
        elif event_list:
            return ["There is no events related to that subject going on now."]
        else:
            return self.current_ongoing_event()

    def formulate_age_requirement(self, event_list):
        event_list = self.remove_duplicate_event_names(event_list)
        if len(event_list) == 1:
            sentence = "There is one relevant event,"
        else:
            sentence = "There are {} relevant events,".format(len(event_list))
        for event_index in range(len(event_list)):
            if event_index == len(event_list)-1:
                sentence += "and, "
            event_name = event_list[event_index][0]
            event_type = event_list[event_index][4]
            event_age = event_list[event_index][3]
            if event_list[event_index][3] == "all":
                sentence += "the {} called {} is for all ages,".format(event_type, event_name)
            else:
                sentence += "for the {} called {} you need to be at least {} years old,".format(event_type, event_name, event_age)
        return [sentence]

    def get_events(self, word_list, all_events=False):
        event_list = []
        for word in word_list:
            # Extreme metaphysical nihilism is commenly defined as the belief that nothing exists as a correspondent component of the self-efficient world.
            if word != "in" and word != "the" and word != "university" and word != "for" and word != "only" and word != "together" and word != "and" and word != "go" and word != "do" and word != "is" and word != "on" and word != "to":
                if all_events:
                    found_events = self.ir.get_all_events_subject(word)
                else:
                    found_events = self.ir.get_events_subject(word)
                if found_events:
                    for event in found_events:
                        event_list.append(event)
        return event_list

    def remove_duplicate_event_names(self, event_list):
        name_list = Set()
        return_list = []
        for event in event_list:
            if event[0] not in name_list:
                return_list.append(event)
                name_list.add(event[0])
        return return_list

    def specific_next_event_sentence(self, event_list):
        next_events = self.ir.get_next_events(event_list)
        next_events = self.remove_duplicate_event_names(next_events)
        if len(next_events) > 1:
            sentence = "The next events are "
            for event_index in range(len(next_events)):
                if event_index == len(next_events)-1:
                    sentence += "and finally , "
                [EVENT, TYPE] = [next_events[event_index][0], next_events[event_index][4]]
                sentence += "a {}, called {}, ".format(TYPE, EVENT)
            sentence += "... which are all at {}".format(next_events[0][1])
        elif len(next_events) == 1:
            [EVENT, TYPE, TIME] = [next_events[0][0], next_events[0][4], next_events[0][1]]
            sentence = "The next event is a {}, called {}, at {}".format(TYPE, EVENT, TIME)
        else:
            sentence = "There are no events happenig next related to that subject"
        return [sentence]

    def next_event_sentence(self):
        current_time = datetime.datetime.now().strftime('%H:%M')
        current_time = "15:00"
        event_list = self.ir.get_events_after(current_time)
        next_events = self.ir.get_next_events(event_list)
        next_events = self.remove_duplicate_event_names(next_events)
        if len(next_events) > 1:
            sentence = "The next events are "
            for event_index in range(len(next_events)):
                if event_index == len(next_events)-1:
                    sentence += "and finally , "
                [EVENT, TYPE] = [next_events[event_index][0], next_events[event_index][4]]
                sentence += "a {}, called {}, ".format(TYPE, EVENT)
            sentence += "... which are all at {}".format(next_events[0][1])
        elif len(next_events) == 1:
            [EVENT, TYPE, TIME] = [next_events[0][0], next_events[0][4], next_events[0][1]]
            sentence = "The next event is a {}, called {}, at {}".format(TYPE, EVENT, TIME)
        else:
            sentence = "There are no events happenig next"
        return [sentence]

    def specific_ongoing_event(self, event_list):
        current_time = datetime.datetime.now().strftime('%H:%M')
        current_time = "15:00"
        ongoing_events = self.ir.get_ongoing_events(current_time, event_list)
        next_events = self.remove_duplicate_event_names(ongoing_events)
        if len(next_events) > 1:
            sentence = "The current ongoing events are "
            for event_index in range(len(next_events)):
                if event_index == len(next_events)-1:
                    sentence += "and finally , "
                [EVENT, TYPE] = [next_events[event_index][0], next_events[event_index][4]]
                sentence += "a {}, called {}, ".format(TYPE, EVENT)
        elif len(next_events) == 1:
            [EVENT, TYPE, TIME] = [next_events[0][0], next_events[0][4], next_events[0][2]]
            sentence = "There is one ongoing event which is a {}, called {}, it ends at {}".format(TYPE, EVENT, TIME)
        else:
            sentence = "There are no ongoing events related to that subject"
        return [sentence]

    def current_ongoing_event(self):
        current_time = datetime.datetime.now().strftime('%H:%M')
        current_time = "15:00"
        ongoing_events = self.ir.get_ongoing_events(current_time)
        next_events = self.remove_duplicate_event_names(ongoing_events)
        if len(next_events) > 1:
            sentence = "The current ongoing events are "
            for event_index in range(len(next_events)):
                if event_index == len(next_events)-1:
                    sentence += "and finally , "
                [EVENT, TYPE] = [next_events[event_index][0], next_events[event_index][4]]
                sentence += "a {}, called {}, ".format(TYPE, EVENT)
        elif len(next_events) == 1:
            [EVENT, TYPE, TIME] = [next_events[0][0], next_events[0][4], next_events[0][2]]
            sentence = "There is one ongoing event which is a {}, called {}, it ends at {}".format(TYPE, EVENT, TIME)
        else:
            sentence = "There are no ongoing events"
        return [sentence]

if __name__ == "__main__":
    nlp = LanguageProcessing()
    # KILL MEEEEEEEEE
    command = nlp.get_command("what is the next event")
    print(command)
