# MAIN File
# Sculpted with love by Thomas Groot en Jonathan Gerbscheid <3

# Imports #
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
# from PIL import Image
import time

# Local modules #
import facedetection
import facerecognition
import speech
import slam
from Sound import locateSound # jonathans naoqi stuff

# Global variables #
# IP = "127.0.0.1"
IP = "pepper.local"

TextToSpeech = None
VideoDevice = None
AudioRecorder = None
AudioDevice = None
SoundLocator = None
Navigation = None
memory = None


#############
# Functions #
#############


# return detected faces
def detect_faces():
    global VideoDevice
    print("Finding faces...")
    face_list = facedetection.detect(VideoDevice)
    return face_list


# Train a set of faces to be associated with a label
def train_recognize_faces(face_list, labels, recognizer=None):
    if recognizer == None:
        recognizer = facerecognition.FaceRecognizer()
    print("Training faces...")
    recognizer.train(face_list, labels)
    return recognizer

# Return names from a list of recognized faces
def recognize_faces(recognizer):
    global VideoDevice
    print("Recognizing faces...")
    recognized_faces = recognizer.recognize(VideoDevice)
    return recognized_faces

# Testing speech synthesis
def speech_test():
    global TextToSpeech
    TextToSpeech.say("Hi thomas")

# Return recognized speech
def speech_recognition(max_tries = 4):
    global AudioRecorder
    global AudioDevice
    print("Recognizing speech...")
    tries = 0
    sentence = ""
    while tries < max_tries and sentence == "":
        sentence = speech.wait_for_voice(AudioRecorder, AudioDevice)
        tries += 1
    return sentence


######################
# Proxy Initializers #
######################


# Allows the robot to say text
def init_textToSpeech():
    global TextToSpeech
    TextToSpeech = ALProxy("ALTextToSpeech", IP, 9559)

# Soundlocator is for locating sound
def init_soundLocalization():
    global SoundLocator
    SoundLocator = locateSound.SoundLocatorModule("SoundLocator")

# Videodevice is for taking images from the videostream
def init_videoDevice():
    global VideoDevice
    VideoDevice = ALProxy("ALVideoDevice", IP, 9559)

# AudioRecorder is for sound recording
def init_audioRecorder():
    global AudioRecorder
    AudioRecorder = ALProxy("ALAudioRecorder", IP, 9559)

# AudioDevice is for sound level registration
def init_audioDevice():
    global AudioDevice
    AudioDevice = ALProxy("ALAudioDevice", IP, 9559)

# Navigation module
def init_navigation():
    global Navigation
    Navigation = ALProxy("ALNavigation", IP, 9559)

########
# Main #
########


def main():
    myBroker = ALBroker("myBroker",
        "0.0.0.0",   # listen to anyone
        0,           # find a free port and use it
        IP,         # parent broker IP
        9559)
    init_soundLocalization()
    while True:
        # do a lot of stuff here
        # finally turn to sound if it was recognized
        # print(locateSound.soundFound)
        # locateSound.soundFound = False
        if SoundLocator.soundFound:
            print("angle found: " + str(SoundLocator.soundAngle))
            SoundLocator.reset_variables()
    print("Done")

# Use the main function
if __name__ == "__main__":
    main()
