# MAIN File
# Sculpted with love by Thomas Groot en Jonathan Gerbscheid <3

# Imports #
from naoqi import ALProxy
# from PIL import Image
import time

# Local modules #
import facedetection
import facerecognition
import speech
import slam

# Global variables #
# IP = "127.0.0.1"
IP = "pepper.local"
cascadePath = "haarcascade_frontalface_default.xml"

#############
# Functions #
#############

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

# Main function that is run once upon startup
def main():
	print("Done")

# Use the main function
if __name__ == "__main__":
	main()