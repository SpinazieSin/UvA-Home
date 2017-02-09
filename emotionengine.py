# -*-coding:utf-8-*-
"""EmotionEngine class file for the media understanding 2017 project.

File name: emotionengine.py
Author: Media Understanding 2017
Date created: 9/2/2017
Date last modified: 9/2/2017
Python Version: 3.4
"""
import numpy as np
import random


class EmotionEngine():
    """
    Emotion engine returns an emotion for a given topic.

    This current implementation does not do anything really except choose
    an emotion at random.
    """

    def __init__(self):
        """Initialize all values."""
        self.emotions = ["Fear",
                         "Anger",
                         "Sadness",
                         "Joy",
                         "Disgust",
                         "Trust",
                         "Anticipation",
                         "Surprise"
                         ]

    def get_emotion(self, topic):
        """Get emotion about given topic."""
        x = np.random.normal(0, 0.5)
        emotion = random.choice(self.emotions)
        return x, emotion

    def __repr__(self):
        """Print article name when object is printed."""
        return "<EmotionEngine, Current emotions: " + str(self.emotions) + ">"
