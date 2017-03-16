# -*-coding:utf-8-*-
"""UserProfile class file for the media understanding 2017 project.

File name: userprofile.py
Author: Media Understanding 2017
Date created: 13/2/2017
Date last modified: 13/2/2017
Python Version: 3.5
"""


class UserProfile():
    """
    Standarized format for user news preference profiles.

    All standard news categories are initialized here, each category
    has a interest rating between 0 and 1, with 1 being the most interesting
    and 0 being not interesting. All values interests are stored in the
    interests dict.
    """

    def __init__(self, username="NAMELESS", facial_features="FILENAME"):
        """Initialize all values."""
        self.keywords = {}
        self.username = username
        self.interests = {}
        self.facial_features = facial_features
        self.interests["top_stories"] = 1.0
        self.interests["world"] = 0.5
        self.interests["africa"] = 0.5
        self.interests["americas"] = 0.5
        self.interests["asia"] = 0.5
        self.interests["europe"] = 0.5
        self.interests["middle_east"] = 0.5
        self.interests["north_america"] = 0.5
        self.interests["money"] = 0.5
        self.interests["technology"] = 0.5
        self.interests["science"] = 0.5
        self.interests["entertainment"] = 0.5
        self.interests["sport"] = 0.5
        self.interests["football"] = 0.5
        self.interests["american_football"] = 0.5
        self.interests["golf"] = 0.5
        self.interests["basketball"] = 0.5
        self.interests["motorsport"] = 0.5
        self.interests["tennis"] = 0.5
        self.interests["travel"] = 0.5
        self.interests["latest"] = 0.5
        self.interests["latin_america"] = 0.5
        self.interests["uk"] = 0.5
        self.interests["england"] = 0.5
        self.interests["northern_ireland"] = 0.5
        self.interests["scotland"] = 0.5
        self.interests["wales"] = 0.5
        self.interests["business"] = 0.5
        self.interests["politics"] = 0.5
        self.interests["education"] = 0.5
        self.interests["art"] = 0.5
        self.interests["companies"] = 0.5
        self.interests["media"] = 0.5
        self.interests["economy"] = 0.5
        self.interests["odd"] = 0.5
        self.interests["lifestyle"] = 0.5
        self.interests["health"] = 0.5
        self.interests["baseball"] = 0.5
        self.interests["environment"] = 0.5
        
    def update_preferences(self, sentiment, article):
        self.interest[article.category] += 0.1 * sentiment
        if sentiment > 1:
            self.keywords.update(article.keywords)
        if sentiment < 0:
            self.keywords -= article.keywords
        self.save_profile()
        return None, [None]


    def __repr__(self):
        """Print user name."""
        return "<Username: " + str(self.username) + ">"
