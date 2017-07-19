# MAIN File
# Sculpted with love by Thomas Groot en Jonathan Gerbscheid <3

# Naoqi Imports #
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

# additional Imports
import math
import time

# Local modules #
import facedetection
import facerecognition
import speech
import slam
from Sound import locateSound # jonathans naoqi stuff
# from PeopleDetection import peopledetector

# Global variables #
# IP = "pepper.local"
IP = "127.0.0.1"
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
def speech_test(text="Hi human"):
	speech_proxy = ALProxy("ALTextToSpeech", IP, PORT)
	speech_proxy.say(text)

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
	motionProxy.wakeUp()
	# if motionProxy.robotIsWakeUp():
	# 	pass
	# else:

def cocktail_party():
	# this function gives an outline of how the cocktail_party function should look

	# STEP 1: ENTER ROOM
		# localize to center of room -> done-ish

	# STEP 2: getting called
	# find a person and approach them

		# person can be calling, waving, or with an arm raised
		# EITHER:
			# sound localize correct person --> done
			# detect random person in room --> done

		# move towards person, -> need distance measure

		# learn person 	-> face recognition done
		#				-> guide person in face recognition

	# STEP 3: taking the order
	# place the order

		# tak additional orders from customers
		# FKIN NOPE
	# STEP 4: sitting person

		# do the same stuff as 2 but for a sitting person that does not call
		# for help
		# sitting people detector: --> filter on shape of detections
		# NOPE

	# STEP 5: placing orders
		# repeat drink, name and person description

	# STEP 6,7,8: we are skipping these
	print("nothing here")


def general_purpose_service():


# Main function that is run once upon startup
def main():
	myBroker = ALBroker("myBroker",
        "0.0.0.0",   # listen to anyone
        0,           # find a free port and use it
        "pepper.local",         # parent broker IP
        9559)
	lifeProxy = ALProxy("ALAutonomousLife", IP, PORT)
	# lifeProxy.setState("disabled")
	print(lifeProxy.getState())
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
	# time.sleep(5)
	speech_test()
	# print("start talking")
	# sentence = speech_recognition()
	# print(sentence)


	# MAIN WHILE LOOP
	while True:
		# do a lot of stuff here
		# speech_recognition

		# finally turn to sound if it was recognized
		if SoundLocator.soundFound:
			# move to the source of the sound
			print("angle found: " + str(SoundLocator.soundAngle))
			motionProxy.moveTo(0.0, 0.0, math.radians(SoundLocator.soundAngle))
			SoundLocator.reset_variables()
	print("Done")

# Use the main function
if __name__ == "__main__":
	main()
