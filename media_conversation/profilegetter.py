# -*-coding:utf-8-*-
"""Preference finding class file for the media understanding 2017 project.

File name: profilegetter.py
Author: Media Understanding 2017
Date created: 22/2/2017
Date last modified: 23/2/2017
Python Version: 3.4
"""
import userprofile
import random
import os
import pickle
import naoqiutils
import platform
if not platform.system() == 'Darwin':  # OS X
    from faceRecognition import facerecognition as facerec
    from faceRecognition import imageRecognition as imrec
    from faceRecognition import trainer
    from speechRecognition import speech as STT


class ProfileGetter():
    """
    ProfileGetter constructs a user profile based on a QA system.

    more text to come
    """

    def __init__(self, news, use_STT=False, use_Nao=False):
        """Initialize all values."""
        self.interests = {"Africa": "africa",
                          "Asia": "asia",
                          "the middle east": "middle_east",
                          "news from the UK": "uk",
                          "sport": "sport",
                          "the environment": "environment",
                          "science": "science",
                          "art": "art",
                          "technology": "technology",
                          "the economy": "economy",
                          "news about politics": "politics",
                          "health": "health",
                          "education": "education",
                          "strange or surprising things": "odd",
                          "the media": "media",
                          "latin america": "latin_america",
                          "business and companies": "business",
                          "travelling": "travel",
                          "lifestyle news": "lifestyle",
                          "european news": "europe",
                          "entertainment": "entertainment",
                          "news about the US:": "north_america"
                          }
        self.newsDB = news
        self.use_STT = use_STT
        self.questions = 10  # amount of question about categories
        self.topics = 3
        self.use_Nao = use_Nao

    def start(self):
        """Init QA, return profile when done."""
        # name is empty if unknown
        known, name = facerec.known_face(use_nao=self.use_Nao, timeout=True)
        fname = ""
        lname = ""
        # First check if the user is already present using face rec.
        if known:
            names = name.split("-")
            fname = names[0]
            lname = names[1]
            self.say("Hi " + fname + "!")
            profile = self.get_profile(name)
        else:
            self.say("Hi! I don't know you, can you stand still for a moment so I can get to know your face?")
            images = imrec.take_photos(use_nao=self.use_Nao)
            self.say("Thank you! Could you now tell me your name?")
            fname, lname = self.get_user_name()
            imrec.saveNewUser(images, fname, lname)
            PATH = "./users/" + fname + "-" + lname
            self.make_folder(PATH)

            # Initialize profile
            profile = userprofile.UserProfile(username=fname + "-" + lname)
            # Start tuning of profile
            response1 = self.question("Can I ask you some questions about the news?")
            if self.positive(response1):
                profile = self.question_categories(profile)

                self.say("Thank you!")
                self.say("I'm now going to ask you about a few current topics, tell me if you think they are interesting.")

                profile = self.question_topics(profile)
                # train the model to include the new user
            self.train_model()

        PATH = "users/" + fname + "-" + lname + "/" + fname + "-" + lname + ".pickle"
        # this makes it work in 2.7 idk why
        ospath = os.path.join(os.path.dirname(__file__), '')
        fullpath = ospath + PATH
        with open(fullpath, 'wb') as handle:
            pickle.dump(profile, handle)
        return profile

    def get_profile(self, name):
        """Get profile with given name."""
        PATH = "users/" + name + "/" + name + ".pickle"

        # this makes it work in 2.7 idk why
        ospath = os.path.join(os.path.dirname(__file__), '')
        fullpath = ospath + PATH
        with open(fullpath, 'rb') as handle:
            profile = pickle.load(handle)
        return profile

    def question_categories(self, profile):
        """Ask questions about categories."""
        random_topics = self.get_random_topics()
        self.say("Are you generally interested")
        for n in range(self.questions):
            response2 = self.question("in " + str(random_topics[n]))

            # adjust interest in user profile
            if self.positive(response2):
                profile.interests[self.interests[random_topics[n]]] += 0.3
            else:
                profile.interests[self.interests[random_topics[n]]] -= 0.3
        return profile

    def question_topics(self, profile):
        """Ask questions about current news topics."""
        counter = 0
        while counter < self.topics:
            artic = random.choice(self.newsDB)
            if profile.interests[artic.category] > 0.5:
                if artic.summary != "":
                    counter += 1
                    # some hacky stuff to print the question in better
                    # format
                    # self.say("is this interesting?")
                    self.say(artic.summary)
                    response3 = self.question(" ")
                    print("(Y/n)")
                    if self.positive(response3):
                        profile.keywords += artic.keywords
        return profile

    def positive(self, response):
        """Return true if response was positive."""
        if response == "y" or response == "yes" or response == "Y" or response == "yeah":
            return True
        else:
            return False

    def train_model(self):
        """Please run the trainer from here, sorry for the inconvenience."""
        trainer.run()

    def get_user_name(self):
        """Ask user for name."""
        fname = ""
        lname = ""
        if self.use_STT:
            self.say("What is your first name?")
            while fname == "":
                fname = STT.wait_for_voice()
                if fname == "":
                    self.say("sorry I didn't catch that.")
            self.say("What is your last name?")
            while lname == "":
                lname = STT.wait_for_voice()
                if lname == "":
                    self.say("sorry I didn't catch that.")
        else:
            self.say("What is your first name?")
            fname = raw_input("First name?\n> ")
            self.say("What is your last name?")
            lname = raw_input("Last name?\n> ")
        return fname, lname

    def make_folder(self, PATH):
        """Make folder with username, ask for new name if unavailable."""
        while os.path.exists(PATH):
            print("that name is not available!")
            name = self.get_user_name()
            PATH = "./users/" + name
        os.makedirs(PATH)

    def get_random_topics(self):
        """Get list of n random categories, n is in self.questions."""
        all_topics = list(self.interests.keys())
        random_topics = []
        for _ in range(self.questions):
            key = random.choice(all_topics)
            all_topics.remove(key)
            random_topics.append(key)
        return random_topics

    def question(self, question):
        """Ask a question, use either SST or command line input."""
        if self.use_STT:
            self.say(question)
            response = STT.wait_for_voice()
        else:
            naoqiutils.speak(question)
            response = raw_input(question + "\n> ")
        return response

    def say(self, phrase):
        """Print phrase or pronounce, depends on the use_STT variable."""
        if self.use_Nao:
            print(phrase)
            naoqiutils.speak(phrase)
        else:
            print(phrase)

    def __repr__(self):
        """Print article name when object is printed."""
        return "<PreferenceFinder, database: " + str(self.newsDB) + ">"
