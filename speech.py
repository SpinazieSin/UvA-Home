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
global recording_counter
recording_counter = 0
IP = "127.0.0.1"

def wait_for_voice(mic, audioproxy):
    """Wait for voice."""
    # obtain audio from microphone, perhaps this should be changed for pepper
    r = sr.Recognizer()
    # try:
    audio = get_audio(r, mic, audioproxy)
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


# @timeout(12)
def get_audio(recognizer, mic, audioproxy):
    """Get audio from microphone, time out after 8 seconds."""
    global recording_counter
    audioproxy.enableEnergyComputation()
    # Start recording
    start_time = time.time()
    mic.startMicrophonesRecording("/home/nao/recordings/speech_recording_" + str(recording_counter) +".wav", "wav", 16000, (0,0,1,0))
    print("Listening...")
    time.sleep(2)
    while True:
        energy = audioproxy.getFrontMicEnergy()
        time.sleep(0.5)
        energy += audioproxy.getFrontMicEnergy()
        time.sleep(0.5)
        final_energy = (energy+audioproxy.getFrontMicEnergy())/3
        print(final_energy)
        if final_energy < 1500.0:
            print("Done listening...")
            break
        if time.time()-start_time > 10.0:
            print(time.time()-start_time)
            print("break")
            break
    mic.stopMicrophonesRecording()
    # initial audio value
    audio = None
    with sr.WavFile("/home/nao/recordings/speech_recording_" + str(recording_counter) +".wav") as source:
        audio = recognizer.record(source)
    recording_counter += 1
    return audio

if __name__ == "__main__":
    AudioRecorder = ALProxy("ALAudioRecorder", IP, 9559)
    AudioDevice = ALProxy("ALAudioDevice", IP, 9559)
    for i in range(4):
        wait_for_voice(AudioRecorder, AudioDevice)