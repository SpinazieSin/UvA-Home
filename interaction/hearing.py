# -*-coding:utf-8-*-
"""Speech file for the media understanding 2017 project.

File name: speech.py
Author: Media Understanding 2017
Date created: 22/2/2017
Date last modified: 22/2/2017
Python Version: 3.4
"""

import speech_recognition as sr
import time

class Hearing:
    def __init__(self, naoqi):
        self.naoqi = naoqi
        self.AudioDevice = self.naoqi.AudioDevice()
        self.AudioRecorder = self.naoqi.AudioRecorder()
        self.recognizer = sr.Recognizer()
        self.energy_breakpoint = 1500.0
        self.minimum_energy = 600.0
        self.timeout = 6.0
        self.hard_timeout = 30.0

    def recognize(self):
        """Attempt to record and recognize speech, returns the audio recognized or an error"""

        audio = self.record_audio()
        if audio == None:
            print("Failed...")
            return "-timeout error-"
        print("Heard...")

        # recognize speech using Google Speech Recognition
        try:
            # to use another API key,
            # use 'r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")'
            # instead of 'r.recognize_google(audio)'
            result = str(self.recognizer.recognize_google(audio))
            print("Found text: " + result)
            return result
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return "-not recognized error-"
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            return "-request error-"
        return "-fatal error-"

    def record_audio(self):
        """Record audio using the robot microphone, time out after self.timeout seconds."""
        self.AudioDevice.enableEnergyComputation()
        # Start recordingaudio
        start_time = time.time()
        hard_timeout_start_time = start_time

        self.AudioDevice.playSine(1500, 30, 0, 0.5)
        time.sleep(0.5)

        self.AudioRecorder.startMicrophonesRecording("/home/nao/recordings/speech_recording.wav", "wav", 16000, (0,0,1,0))
        print("Listening...")
        time.sleep(2)
        while True:
            energy = self.AudioDevice.getFrontMicEnergy()
            print("ENERGY = " + str(energy)) ########################################################################

            if energy > self.minimum_energy:
                print("Detected something...")
                time.sleep(0.5)
                energy += self.AudioDevice.getFrontMicEnergy()
                time.sleep(0.5)
                final_energy = (energy+self.AudioDevice.getFrontMicEnergy())/3
                print("Front mic energy level: " + str(final_energy))
                if final_energy < self.energy_breakpoint:
                    self.AudioDevice.playSine(1000, 30, 0, 0.5)
                    print("Done listening...")
                    break
                if time.time()-start_time > self.timeout:
                    self.AudioRecorder.stopMicrophonesRecording()
                    print(time.time()-start_time)
                    return None
            else:
                time.sleep(0.2)
                if time.time()-hard_timeout_start_time > self.hard_timeout:
                    print("No voice activity...")
                    self.AudioRecorder.stopMicrophonesRecording()
                    return None
                if time.time()-start_time > self.timeout:
                    print("Nothing heard, listening again...")
                    start_time = time.time()
                    self.AudioRecorder.stopMicrophonesRecording()
                    time.sleep(0.1)
                    self.AudioRecorder.startMicrophonesRecording("/home/nao/recordings/speech_recording.wav", "wav", 16000, (0,0,1,0))

        self.AudioRecorder.stopMicrophonesRecording()
        audio = self.get_recording()
        return audio

    def get_recording(self):
        """Gets the most recent audio recording from the robot"""
        with sr.WavFile("/home/nao/recordings/speech_recording.wav") as source:
            audio = self.recognizer.record(source)
        return audio
