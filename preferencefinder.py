# -*-coding:utf-8-*-
"""Preference finding class file for the media understanding 2017 project.

File name: emotionengine.py
Author: Media Understanding 2017
Date created: 9/2/2017
Date last modified: 9/2/2017
Python Version: 3.4
"""
import numpy as np
import userprofile
import articlesearch
import random


class PreferenceFinder():
    """
    PreferenceFinder constructs a user profile based on a QA system.

    more text to come
    """

    def __init__(self, news):
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
                          "business and companies": "business"
                          }
        # self.interests["top_stories"] = 1.0
        # self.interests["world"] = 0.5
        # self.interests["africa"] = 0.5
        # self.interests["americas"] = 0.5
        # self.interests["asia"] = 0.5
        # self.interests["europe"] = 0.5
        # self.interests["middle_east"] = 0.5
        # self.interests["north_america"] = 0.5
        # self.interests["money"] = 0.5
        # self.interests["technology"] = 0.5
        # self.interests["science"] = 0.5
        # self.interests["entertainment"] = 0.5
        # self.interests["sport"] = 0.5
        # self.interests["football"] = 0.5
        # self.interests["golf"] = 0.5
        # self.interests["motorsport"] = 0.5
        # self.interests["tennis"] = 0.5
        # self.interests["travel"] = 0.5
        # self.interests["latest"] = 0.5
        # self.interests["latin_america"] = 0.5
        # self.interests["uk"] = 0.5
        # self.interests["england"] = 0.5
        # self.interests["northern_ireland"] = 0.5
        # self.interests["scotland"] = 0.5
        # self.interests["wales"] = 0.5
        # self.interests["business"] = 0.5
        # self.interests["politics"] = 0.5
        # self.interests["education"] = 0.5
        # self.interests["art"] = 0.5
        # self.interests["media"] = 0.5
        # self.interests["economy"] = 0.5
        # self.interests["odd"] = 0.5
        # self.interests["lifestyle"] = 0.5
        # self.interests["health"] = 0.5
        # self.interests["environment"] = 0.5
        self.newsDB = news

    def question_answer(self):
        """Init QA, return true when done."""
        # searcher = articlesearch.ArticleSearch()
        questions = 10
        topics = 10
        all_topics = list(self.interests.keys())

        random_topics = []
        for _ in range(questions):
            key = random.choice(all_topics)
            all_topics.remove(key)
            random_topics.append(key)

        name = input("Hi! can you tell me your name?\n")
        profile = userprofile.UserProfile(username=name)

        response1 = input("Can I ask you some questions about the news? (Y/n)\n")
        if self.positive(response1):
            for n in range(questions):
                response2 = input("Are you generally interested in " +
                                  str(random_topics[n]) + "\n")
                if self.positive(response2):
                    profile.interests[self.interests[random_topics[n]]] += 0.3
                else:
                    profile.interests[self.interests[random_topics[n]]] -= 0.3
        print("Thank you! ")
        print("I'm now going to ask you about a few current topics, tell me" +
              " if you think they are interesting.")

        print(len(self.newsDB))
        while topics > 0:
            artic = random.choice(self.newsDB)
            print("checking article.")
            if profile.interests[artic.category] > 0.5:
                if artic.summary != "":
                    topics -= 1
                    responsy = input("Is this interesting?\n" +
                                     artic.summary + "\n")
                    if self.positive(responsy):
                        profile.keywords.append(artic.keywords)

        return profile

    def positive(self, response):
        """Return true if response was positive."""
        if response == "Y" or "y" or "yes" or "Yes" or "YES":
            return True
        else:
            return False

    def __repr__(self):
        """Print article name when object is printed."""
        return "<PreferenceFinder, database: " + str(self.newsDB) + ">"
