import time
from random import randint

class Speech:

    current_name = None
    gestures = ["^start(animations/Stand/Gestures/You_1)",
                "^start(animations/Stand/Gestures/Explain_1)",
                "^start(animations/Stand/Gestures/Explain_2)",
                "^start(animations/Stand/Gestures/Explain_7)",
                "^start(animations/Stand/Gestures/Explain_8)",
                "^start(animations/Stand/Emotions/Neutral/Embarrassed_1)",
                "^start(animations/Stand/Gestures/Yes_1)",
                "^start(animations/Stand/Gestures/Enthusiastic_3)",
                "^start(animations/Stand/Gestures/Enthusiastic_5)",
                "^start(animations/Stand/Gestures/ShowSky_1)",
                "^start(animations/Stand/Gestures/Hey_1)",
                "^start(animations/Stand/Gestures/YouKnowWhat_1)",
                "^start(animations/Stand/Gestures/YouKnowWhat_5)"]


    # sets the volume to a default value
    def __init__(self, session):
        self.animated_speech = session.service("ALAnimatedSpeech")
        self.posture = session.service("ALRobotPosture")



    def say(self, sentence, animations=[]):
        for i in animations:
            sentence = sentence.format(self.gestures[i])
        self.animated_speech.say(sentence)
        self.posture.goToPosture("Stand", 1.0)
        
