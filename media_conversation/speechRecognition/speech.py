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
from timeout import timeout
from naoqi import ALProxy

# def wait_for_voice():
#     """Wait for voice."""
#     # obtain audio from microphone, perhaps this should be changed for pepper
#     print("Listening")
#     r = sr.Recognizer()
#     try:
#         audio = get_audio(r)
#     except:
#         print("Something went wrong while retrieving audio")
#         return ""

#     print("I heard you!")
#     # recognize speech using Google Speech Recognition
#     try:
#         # for testing purposes, we're just using the default API key
#         # to use another API key,
#         # use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
#         # instead of `r.recognize_google(audio)`
#         result = r.recognize_google(audio)
#         print("Found text: " + result)
#         return result
#     except sr.UnknownValueError:
#         print("Google Speech Recognition could not understand audio")
#         return ""
#     except sr.RequestError as e:
#         print("Could not request results from Google Speech Recognition service; {0}".format(e))
#         return ""
#     except KeyError as e:
#         print("uhhh.... keyerror? I don't know why this happens just continue please")
#         return ""


# @timeout(8)
# def get_audio(recognizer):
#     """Get audio from microphone, time out after 8 seconds."""
#     # with sr.Microphone() as source:
#     #     audio = recognizer.listen(source)
#     mic = ALProxy("ALAudioRecorder", "127.0.0.1", 9559)
#     mic.startMicrophonesRecording("~/recent_recording.wav", "wav", 16000, (0,0,1,0))
#     time.sleep(2)
#     mic.stopMicrophonesRecording()
#     time.sleep(1)
#     return audio

def wait_for_voice():
    """Wait for voice."""
    # obtain audio from microphone, perhaps this should be changed for pepper
    r = sr.Recognizer()
    # try:
    audio = get_audio(r)
    # except:
    #     print("Something went wrong while retrieving audio")
    #     return ""

    print("Heard...")
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
    except KeyError as e:
        print("uhhh.... keyerror? I don't know why this happens just continue please")
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
