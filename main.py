# MAIN File
# Sculpted with love by Thomas Groot en Jonathan Gerbscheid <3

# Naoqi Imports #
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

# additional Imports
import math

# Local modules #
import facedetection
import facerecognition
import speech
import soundlocalization # thomas stuff
from Sound import locateSound # jonathans naoqi stuff
# from PeopleDetection import peopledetector

# Global variables #
IP = "pepper.local"
PORT = 9559
cascadePath = "haarcascade_frontalface_default.xml"

SoundLocator = None
memory = None
motionProxy  = None
postureProxy = None
camProxy = None
pplDetectionargs = None


#############
# Functions #
#############
def setup_people_detection():
	global pplDetectionargs
	global camProxy
	camProxy = ALProxy("ALVideoDevice", IP, PORT)
	pplDetectionargs = peopledetector.setup_network()

def detect_people():
	return peopledetector.detect_people(camProxy, *pplDetectionargs)


# return detected faces
def detect_faces():
	print("Finding faces...")
	face_list = facedetection.detect()
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
	print("Recognizing faces...")
	recognized_faces = recognizer.recognize()
	return recognized_faces

# Testing speech synthesis
def speech_test():
	speech_proxy = ALProxy("ALTextToSpeech", IP, 9559)
	speech_proxy.say("Hi thomas")

# Return recognized speech
def speech_recognition(max_tries = 4):
	print("Recognizing speech...")
	tries = 0
	sentence = ""
	while tries < max_tries and sentence == "":
		sentence = speech.wait_for_voice()
		tries += 1
	return sentence

def init_soundLocalization():
	global SoundLocator
	SoundLocator = locateSound.SoundLocatorModule("SoundLocator")


def init_navigation():
	global motionProxy
	global postureProxy
	motionProxy = ALProxy("ALMotion", IP, PORT)
	postureProxy = ALProxy("ALRobotPosture", IP, PORT)


# Main function that is run once upon startup
def main():
	# faces = detect_faces()
	# if len(faces) > 0:
	# 	print("Hi thomas")
	# print(speech_recognition(1))
	# face_list = detect_faces()
	# if len(face_list) > 0:
	# 	print(len(face_list))
	# 	labels = []
	# 	for i in face_list:
	# 		labels.append(0)
	# 	recognizer = train_recognize_faces(face_list, labels)
	# 	recognized_faces_list = recognize_faces(recognizer)
	# 	print(recognized_faces_list)
	# else:
	# 	print("Failed")
	# print(soundlocalization.localize_sound(40, True))
	myBroker = ALBroker("myBroker",
        "0.0.0.0",   # listen to anyone
        0,           # find a free port and use it
        "pepper.local",         # parent broker IP
        9559)
	init_soundLocalization()
	init_navigation()
	# test_main.main()
	# setup_people_detection()
	# look around for a crowd
    # x     = 0.0
    # y     = 0.0
    # theta = 0.5
    # frequency = 1.0
    # motionProxy.moveToward(x, y, theta, [["Frequency", frequency]])
	# # find ppl
	# motionProxy.stopMove()


	# while True:
	# 	# do a lot of stuff here
	# 	# finally turn to sound if it was recognized
	# 	# print(locateSound.soundFound)
	# 	# locateSound.soundFound = False
	# 	if SoundLocator.soundFound:
	# 		# move to the source of the sound
	# 		print("angle found: " + str(SoundLocator.soundAngle))
	# 		motionProxy.moveTo(0.0, 0.0, math.radians(SoundLocator.soundAngle))
	# 		SoundLocator.reset_variables()


	print("Done")

# Use the main function
if __name__ == "__main__":
	main()
