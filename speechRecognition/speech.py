# -*-coding:utf-8-*-
"""Speech file for the media understanding 2017 project.

File name: speech.py
Author: Media Understanding 2017
Date created: 22/2/2017
Date last modified: 22/2/2017
Python Version: 3.4
"""
import speech_recognition as sr
import sys
import os
import threading
import time
dir_path = os.path.dirname(os.path.realpath(__file__))
up_dir = os.path.dirname(os.path.dirname(dir_path))
from timeout import timeout
import naoqiutils


def wait_for_voice():
    """Wait for voice."""
    # obtain audio from microphone, perhaps this should be changed for pepper
    naoqiutils.play_sine(300)
    r = sr.Recognizer()
    try:
        audio = get_audio(r)
    except:
        naoqiutils.play_sine(50)
        print("Something went wrong while retrieving audio")
        return ""

    print("I heard you!")
    naoqiutils.play_sine(200)
    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key,
        # use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        result = r.recognize_google(audio)
        print("Found text: " + result)
        return result
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return ""
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return ""


@timeout(8)
def get_audio(recognizer):
    """Get audio from microphone, time out after 8 seconds."""
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    return audio


if __name__ == '__main__':
    print("this main does nothing")
    # do nothing
