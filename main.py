# MAIN File
# Sculpted with love by Thomas Groot en Jonathan Gerbscheid <3

# Imports #
from naoqi import ALProxy
# from PIL import Image

# Local modules #
import facedetection

# Global variables #
IP = "127.0.0.1"
cascadePath = "haarcascade_frontalface_default.xml"

#############
# Functions #
#############

# return detected faces
def detect_faces():
	face_list = facedetection.detect()
	return face_list

# Testing speech
def speech_test():
	speech_proxy = ALProxy("ALTextToSpeech", IP, 9559)
	speech_proxy.say("Hi thomas")


# Main function that is run once upon startup
def main():
	faces = detect_faces()
	if len(faces) > 0:
		print("Hi thomas")


# Use the main function
if __name__ == "__main__":
	main()