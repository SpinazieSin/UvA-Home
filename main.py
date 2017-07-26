# MAIN File
# Sculpted with love by Thomas Groot en Jonathan Gerbscheid <3

# Naoqi Imports #
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

# additional Imports
import math
import time
import sys
import Image
import numpy
import cv2
# Local modules #
import facedetection
import facerecognition
import speech
import slam
import questions_answers
import language_processing
from Sound import locateSound # jonathans naoqi stuff
from PeopleDetection import peopledetector

# Global variables #
# IP = "127.0.0.1"
# IP = "pepper.local"
# IP = "146.50.60.15"
IP = "192.168.131.13"
PORT = 9559

TextToSpeech = None
VideoDevice = None
AudioRecorder = None
AudioDevice = None
SoundLocator = None
Navigation = None
Localizer = None
memory = None
motionProxy  = None
postureProxy = None
pplDetectionargs = None


#############
# Functions #
#############


# jonathan comment dit
def setup_people_detection():
    global pplDetectionargs
    pplDetectionargs = peopledetector.setup_network()

# jonathan comment dit
def detect_people():
    detections = peopledetector.detect_people(VideoDevice, *pplDetectionargs)
    outlist = []
    for detection in detections:
        outlist.append([detection[0][0], detection[0][1], detection[1][0], detection[1][1]])
    return outlist

# return detected faces
def make_face_database(tracking=False):
    global VideoDevice
    if tracking:
        if motionProxy == None:
            init_localization()
        print("Finding faces...")
        face_list = facedetection.collect_faces(VideoDevice, motionProxy)
    else:
        print("Finding faces...")
        face_list = facedetection.collect_faces(VideoDevice)
    return face_list

# Detects faces in one image
def detect_faces():
    global VideoDevice
    face_list = facedetection.detect_once(VideoDevice)
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
def robot_say(text="Hi human"):
    global TextToSpeech
    TextToSpeech.say(text)

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
    SoundLocator = locateSound.SoundLocatorModule("SoundLocator", IP, PORT)

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

def init_motion():
    global motionProxy
    global postureProxy
    motionProxy = ALProxy("ALMotion", IP, PORT)
    postureProxy = ALProxy("ALRobotPosture", IP, PORT)
    motionProxy.wakeUp()

def init_localization():
    global Localizer
    Localizer = slam.Localization(Navigation)


########
# Main #
########

def turn_to_person():
    detectioncounter = 0
    while True:
        peopleList = detect_people()
        if len(peopleList) > 0:
            boxindex = get_biggest_box_index(peopleList)
            width = peopleList[boxindex][2] - peopleList[boxindex][0]
            height = peopleList[boxindex][3] - peopleList[boxindex][1]
            size = width * height
            if size > 10000:
                detectioncounter += 1
                # turn to person
                box = peopleList[boxindex]
                print(box)
                print(box[0]/2.0)
                boxcenter = box[0] +  ((box[2] - box[0])/2.0)
                print(boxcenter)
                im_width = 640

                dwidth = im_width/55.20
                pdiff = im_width/2.0 - boxcenter
                turn = (math.radians(pdiff / dwidth))
                print("angle: " + str(turn))
                motionProxy.moveTo(0.0, 0.0, turn)
                if detectioncounter > 3:
                    robot_say("found you!")
                    return peopleList
            else:
                detectioncounter = 0
                # motionProxy.moveTo(0.0, 0.0, math.radians(30))
        else:
            detectioncounter = 0
            # motionProxy.moveTo(0.0, 0.0, math.radians(30))

def turn_to_sound():
    SoundLocator.reset_variables()
    while True:
        if SoundLocator.soundFound:
            # move to the source of the sound
            print("angle found: " + str(SoundLocator.soundAngle))
            motionProxy.moveTo(0.0, 0.0, math.radians(SoundLocator.soundAngle))
            SoundLocator.reset_variables()
            break


def get_biggest_box_index(boxlist):
    index = 0
    maxsize = 0
    for i in range(len(boxlist)):
        width = boxlist[i][2] - boxlist[i][0]
        height = boxlist[i][3] - boxlist[i][1]
        size = width * height
        if size > maxsize:
            maxsize = size
            index = i
    return index


def move_forward_until_stuck():
    pass


def speech_and_person():
    # wait for door to open

    # move forward to middle of room

    robot_say("I want to play a riddle game")
    time.sleep(10)
    motionProxy.moveTo(0.0, 0.0, math.radians(180))



def cocktail_party():
    qa = questions_answers.QA()
    # this function gives an outline of how the cocktail_party function should look
    # init_localization()
    # Localizer.stop_localization()
    # Navigation.loadExploration("/home/nao/.local/share/Explorer/2017-07-20T123155.689Z.explo")
    # Localizer.start_localization()
	# STEP 1: ENTER ROOM
		# localize to center of room -> done-ish
    # Localizer.move_to([0,0])

	# STEP 2: getting called
	# find a person and approach them
    setup_people_detection()

    # localize using sound
    # init_soundLocalization()
    # turn_to_sound()

    # localize using people detection
    peopleList = turn_to_person()
    # move to person
    # move_straight_until_stuck

        # person can be calling, waving, or with an arm raised
        # EITHER:
            # sound localize correct person --> done
            # detect random person in room --> done

        # move towards person, -> need distance measure

        # learn person     -> face recognition done
        robot_say(qa.ask_for_name())
        sentence = speech_recognition()
        if len(sentence) > 0:
        person_index = 0
        face_list = make_face_database(True)
        label_list = []
        for face in face_list:
            label_list.append(person_index)
        # If a recognizer exists, use that recognizer
        recognizer = train_recognize_faces(face_list, label_list)
        robot_say("I learned your face!")
        #                -> guide person in face recognition

    # STEP 3: taking the order
    robot_say(qa.ask_for_drink())
    sentence = speech_recognition()
    if len(sentence) > 0:
        candidate_drink_list = language_processing.get_all_drinks(sentence)
        if len(candidate_drink_list) > 0:
            drink_list = candidate_drink_list

    # place the order

        # take additional orders from customers
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
    print("nothing here")


def navigation_things():
    """this method does nothing except hold the navigation code that I am still
    working on, but that is not allowed in the main :)."""
    Localizer.explore(1)
    Localizer.save_exploration()
    result_map = Navigation.getMetricalMap()
    map_width = result_map[1]
    map_height = result_map[2]
    img = numpy.array(result_map[4]).reshape(map_width, map_height)
    img = (100 - img) * 2.55 # from 0..100 to 255..0
    img = numpy.array(img, numpy.uint8)
    cv2.imwrite("robocup-nagoya.png", img)
    # Localizer.stop_exploration()
    # Localizer.explore(1)
    # Navigation.stopLocalization()
    # # Localizer.start_localization()
    # # Localizer.load_exploration("/home/nao/.local/share/Explorer/2017-07-19T163238.071Z.explo")
    # Navigation.loadExploration("/home/nao/.local/share/Explorer/2017-07-20T123155.689Z.explo")
    # # Navigation.getMetricalMap()
    # # print("path: " + str(Localizer.map_path))
    # # Localizer.load_exploration("2017-07-20T123155.689Z.explo")
    # result_map = Navigation.getMetricalMap()
    # map_width = result_map[1]
    # map_height = result_map[2]
    # img = numpy.array(result_map[4]).reshape(map_width, map_height)
    # img = (100 - img) * 2.55 # from 0..100 to 255..0
    # img = numpy.array(img, numpy.uint8)
    # # cv2.imwrite("iismap2.png", img)
    # # pilimage = Image.frombuffer('L',  (map_width, map_height), img, 'raw', 'L', 0, 1)
    #
    # # for i in range(120):
    # #     for j in range(120):
    # #         img[i][j] = 1
    # #         cv2.imshow("map", img)
    # #         cv2.waitKey(1)
    #
    # est_position_maybe = Navigation.relocalizeInMap([0,0])
    # # est_position = Navigation.getRobotPositionInMap()
    # while True:
    #     # Localizer.relocalize([0,0])
    #     # est_position = Navigation.getRobotPositionInMap()
    #     est_position = Navigation.relocalizeInMap([0,0])
    #     print(est_position[1][0])
    #     a = est_position[1][0][0]
    #     b = est_position[1][0][1]
    #     x = map_width * a
    #     y = map_height * b
    #     print("adjusted: " + str(x) + ", " + str(y))
    #     Navigation.startLocalization()
    #     Navigation.navigateToInMap([0.,0.])
    #
    # # print("start talking")
    # # sentence = speech_recognition()
    # # print(sentence)
    # Localizer.start_localization()
    # Localizer.relocalize([0.,0.])
    # print("path: " + str(Localizer.map_path))
    # # Localizer.move_to([-1., -1.])
    # print("estimate location: " + str(Localizer.get_robot_position()))
    # Localizer.stop_exploration()


# Main function that is run once upon startup
def main():
    lifeProxy = ALProxy("ALAutonomousLife", IP, PORT)
    # lifeProxy.setState("disabled")
    print("AutonomousLife: " + lifeProxy.getState())
    init_soundLocalization()
    init_navigation()
    init_textToSpeech()
    init_videoDevice()
    init_motion()
    init_audioDevice()
    init_audioRecorder()
    # init_localization()

    # correct head angle for long distances
    # currentAngle = motionProxy.getAngles("HeadYaw", True)[0]
    # motionProxy.setAngles(["HeadPitch"], currentAngle + 0.08, 0.2)

    # not finished
    cocktail_party()


    # MAIN WHILE LOOP
    while True:
        # do a lot of stuff here
        peopleList = detect_people()
        print("found " + str(len(peopleList)) + " people!")
       # Localizer.get_map()
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
