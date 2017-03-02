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
# import speechRecognition.speech as STT
from faceRecognition import facerecognition as facerec
from faceRecognition import imageRecognition as imrec
from faceRecognition import trainer


class ProfileGetter():
    """
    ProfileGetter constructs a user profile based on a QA system.

    more text to come
    """

    def __init__(self, news, use_STT=False, voiced=False):
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
        self.voiced = voiced
        self.questions = 10  # amount of question about categories
        self.topics = 10

    def start(self):
        """Init QA, return profile when done."""
        # name is empty if unknown
        known, name = facerec.known_face()

        # First check if the user is already present using face rec.
        if known:
            print("Hi " + name + "!")
            PATH = "users/" + name + "/" + name + ".pickle"

            # this makes it work in 2.7 idk why
            ospath = os.path.join(os.path.dirname(__file__), '')
            fullpath = ospath + PATH
            with open(fullpath, 'rb') as handle:
                profile = pickle.load(handle)
        else:
            images = imrec.take_photos()
            print("Hi! can you tell me your name?")
            fname, lname = self.get_user_name()
            imrec.saveNewUser(images, fname, lname)
            PATH = "./users/" + fname + "-" + lname
            self.make_folder(PATH)

            random_topics = self.get_random_topics()
            # Initialize profile
            profile = userprofile.UserProfile(username=fname + "-" + lname)

            response1 = self.question("Can I ask you some questions about the\
             news? (Y/n)")
            if self.positive(response1):
                for n in range(self.questions):
                    response2 = self.question("Are you generally interested \
                    in " + str(random_topics[n]))

                    # adjust interest in user profile
                    if self.positive(response2):
                        profile.interests[self.interests[random_topics[n]]] +=\
                                                                            0.3
                    else:
                        profile.interests[self.interests[random_topics[n]]] -=\
                                                                            0.3
            self.say("Thank you!")
            self.say("I'm now going to ask you about a few current topics, tell\
             me if you think they are interesting.")

            counter = 0
            while counter < self.topics:
                artic = random.choice(self.newsDB)
                if profile.interests[artic.category] > 0.5:
                    if artic.summary != "":
                        counter += 1
                        # some hacky stuff to print the question in better
                        # format
                        self.say("is this interesting?")
                        print(artic.summary)
                        response3 = self.question("(Y/n)")
                        if self.positive(response3):
                            profile.keywords.append(artic.keywords)

            PATH = "users/" + fname + "-" + lname + "/" + fname + "-" + lname + ".pickle"
            # this makes it work in 2.7 idk why
            ospath = os.path.join(os.path.dirname(__file__), '')
            fullpath = ospath + PATH
            with open(fullpath, 'wb') as handle:
                pickle.dump(profile, handle)
            self.train_model()
        return profile

    def positive(self, response):
        """Return true if response was positive."""
        if response == "y" or response == "yes" or response == "Y":
            return True
        else:
            return False

    def train_model(self):
        """Please run the trainer from here, sorry for the inconvenience."""
        trainer.run()

    def say_phrase(phrase):
        """Pronounce given phrase."""
        print("no speech synthesis implemented yet.")

    def get_user_name(self):
        """Ask user for name."""
        name = ""
        if self.use_STT:
            while name != "":
                name = STT.wait_for_voice()
                if name == "":
                    print("sorry I didn't catch that.")
        else:
            fname = raw_input("Hi! can you tell me your first name?\n")
            lname = raw_input("Hi! can you tell me your last name?\n")
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
            response = raw_input(question + "\n")
        return response

    def say(self, phrase):
        """Print phrase or pronounce, depends on the use_STT variable."""
        if self.voiced:
            # not implemented
            print("VOICED NOT IMPLEMENTED YET!")
            print(phrase)
        else:
            print(phrase)

    def __repr__(self):
        """Print article name when object is printed."""
        return "<PreferenceFinder, database: " + str(self.newsDB) + ">"