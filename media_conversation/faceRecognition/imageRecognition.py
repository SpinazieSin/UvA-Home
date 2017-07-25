#!/usr/bin/env python2
"""this file is used for taking training photos for new users.

File name: imagerecognition.py
Author: Media Understanding 2017
Date created: 2/3/2017
Date last modified: 2/3/2017
Python Version: 2.7
"""

import cv2
import os
import pickle
import sys
import numpy as np
from PIL import Image
from sklearn.mixture import GMM
import openface
from naoqi import ALProxy
# forgive my hackeries but this should work on all or computers
dir_path = os.path.dirname(os.path.realpath(__file__))
up_dir = os.path.dirname(os.path.dirname(dir_path))

sys.path.append(up_dir)
import headmotions


np.set_printoptions(precision=2)

IMG_DIM = 96
WIDTH = 320
HEIGHT = 240
THRESHOLD = 0.65
IMAGECOUNT = 10
IP = "192.168.131.13"
PORT = 9559
motionProxy = ALProxy("ALMotion", IP, PORT)
resolution = 2    # VGA
colorSpace = 11  # RGB

# def run():
    # # Start recognising
    # person, images = identifyPerson()
    #
    # # Identify
    # if person == "_unknown":
    #     person = saveNewUser(images)
    #
    # # start program
    # print "Lets play, " + person


def saveNewUser(images, fName, lName):
    """"Create new directory for user and save the photos."""
    fileDir = os.path.join(os.path.dirname(__file__), '')
    fileDir = os.path.dirname(os.path.realpath(__file__))
    trainDir = os.path.join(fileDir, 'training-images')
    print("traindir:" + str(trainDir))
    directory = os.path.join(trainDir, fName + "-" + lName)
    n = 0
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        n = max([int(d.split("-")[2]) for d in os.listdir(trainDir)
            if d.startswith(fName + "-" + lName)] + [0]) + 1
        os.makedirs(directory)

    for i, img in enumerate(images):
        print("iteration over images")
        goodimg = Image.fromarray(img)
        goodimg.save(directory + "/image" + str(i) + ".png")
    #     cv2.imwrite(directory + "/image" + str(i) + ".png", img)
    return fName + "-" + lName + "-" + str(n)


def take_photos(use_nao=True):
    """Take images containing faces until IMAGECOUNT is reached."""
    fileDir = os.path.dirname(os.path.realpath(__file__))
    print(fileDir)
    modelDir = os.path.join(fileDir, 'models')
    dlibModelDir = os.path.join(modelDir, 'dlib')
    openfaceModelDir = os.path.join(modelDir, 'openface')

    dlibFacePredictor = os.path.join(dlibModelDir,
        "shape_predictor_68_face_landmarks.dat")
    networkModel = os.path.join(openfaceModelDir, 'nn4.small2.v1.t7')
    cuda = False

    align = openface.AlignDlib(dlibFacePredictor)
    net = openface.TorchNeuralNet(networkModel, imgDim=IMG_DIM, cuda=cuda)
    if not use_nao:
        video_capture = cv2.VideoCapture(0)
        video_capture.set(3, WIDTH)
        video_capture.set(4, HEIGHT)

    # Check if person is known
    picturesTaken = 0
    # possiblePersons = collections.Counter()
    images = []
    while (picturesTaken < IMAGECOUNT):
        if use_nao:
            naoqi_frame = get_image()
            # naoqi_frame is an rgb image, I checked this.
            frame = np.array(naoqi_frame)
        else:
            # line for using with webcams
            video_capture = cv2.VideoCapture(0)
            video_capture.set(3, WIDTH)
            video_capture.set(4, HEIGHT)
            ret, frame = video_capture.read()
            print("photo taken")

        persons, confidences = infer(frame, align, net, use_nao)
        for i, c in enumerate(confidences):
            if c <= THRESHOLD:
                persons[i] = "_unknown"

        if len(persons) == 0:
            print "No person detected"
            continue

        if persons[0] == "_unknown":
            print("found unknown person")
            images.append(frame)
            picturesTaken += 1

        #     print "P: " + str(persons) + " C: " + str(confidences)
        #     possiblePersons[persons[i]] += 1
        # Quit the program on the press of key 'q'
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
    if not use_nao:
        video_capture.release()
        cv2.destroyAllWindows()

    # person = possiblePersons.most_common(1)[0][0]
    return images


def infer(img, align, net, use_nao):
    ospath = os.path.join(os.path.dirname(__file__), '')
    classifierModel = ospath + '/generated-embeddings/classifier.pkl'

    with open(classifierModel, 'r') as f:
        (le, clf) = pickle.load(f)  # le - label and clf - classifer

    reps = getRep(img, align, net, use_nao)
    persons = []
    confidences = []
    for rep in reps:
        try:
            rep = rep.reshape(1, -1)
        except:
            print "No Face detected"
            return (None, None)
        predictions = clf.predict_proba(rep).ravel()
        # print predictions
        maxI = np.argmax(predictions)
        # max2 = np.argsort(predictions)[-3:][::-1][1]
        persons.append(le.inverse_transform(maxI))
        # print str(le.inverse_transform(max2)) + ": "+str( predictions [max2])
        # ^ prints the second prediction
        confidences.append(predictions[maxI])
        # print("Predict {} with {:.2f} confidence.".format(person, confidence))
        if isinstance(clf, GMM):
            dist = np.linalg.norm(rep - clf.means_[maxI])
            print("  + Distance from the mean: {}".format(dist))
            pass
    return (persons, confidences)

def getRep(bgrImg, align, net, use_nao):
    if bgrImg is None:
        raise Exception("Unable to load image/frame")

    # rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_RGB2BGR)
    rgbImg = bgrImg

    # Get the largest face bounding box
    # bb = align.getLargestFaceBoundingBox(rgbImg) #  Bounding box

    # Get all bounding boxes
    bb = align.getAllFaceBoundingBoxes(rgbImg)

    if bb is None:
        # raise Exception("Unable to find a face: {}".format(imgPath))
        return None
    if len(bb) > 0 and use_nao:
        # print("image size: " + str(rgbImg.shape))
        # print("position of face: " + str(bb[0].center()))
        center = bb[0].center()
        width = rgbImg.shape[0]
        height = rgbImg.shape[0]
        headmotions.move_head(center.x, center.y, width, height, IP, motionProxy)

    alignedFaces = []
    for box in bb:
        alignedFaces.append(
            align.align(
                IMG_DIM,
                rgbImg,
                box,
                landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE))

    if alignedFaces is None:
        raise Exception("Unable to align the frame")
    reps = []
    for alignedFace in alignedFaces:
        reps.append(net.forward(alignedFace))

    # print reps
    return reps

    # def identifyPerson():
    #     video_capture = cv2.VideoCapture(0)
    #     video_capture.set(3, WIDTH)
    #     video_capture.set(4, HEIGHT)
    #
    #     # Check if person is known
    #     picturesTaken = 0
    #     possiblePersons = collections.Counter()
    #     images = []
    #     while (picturesTaken < 10):
    #         ret, frame = video_capture.read()
    #         images.append(frame)
    #         persons, confidences = infer(frame)
    #         if len(persons) == 0:
    #             picturesTaken -= 1
    #             print "No person detected"
    #
    #         for i, c in enumerate(confidences):
    #             if c <= THRESHOLD:
    #                 persons[i] = "_unknown"
    #             print "P: " + str(persons) + " C: " + str(confidences)
    #             possiblePersons[persons[i]] += 1
    #         cv2.putText(frame, "P: {} C: {}".format(persons, confidences),
    #                     (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    #         cv2.imshow('', frame)
    #         # Quit the program on the press of key 'q'
    #         if cv2.waitKey(1) & 0xFF == ord('q'):
    #             break
    #         picturesTaken += 1
    #     video_capture.release()
    #     cv2.destroyAllWindows()
    #
    #     person = possiblePersons.most_common(1)[0][0]
    #     return person, images


def get_image():
    videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)
    # Get a camera image.
    # image[6] contains the image data passed as an array of ASCII chars.
    naoImage = camProxy.getImageRemote(videoClient)

    imageWidth = naoImage[0]
    imageHeight = naoImage[1]
    array = naoImage[6]

    im = Image.fromstring("RGB", (imageWidth, imageHeight), array)
    camProxy.unsubscribe(videoClient)
    return im

if __name__ == '__main__':
    fileDir = os.path.dirname(os.path.realpath(__file__))
    modelDir = os.path.join(fileDir, 'models')
    dlibModelDir = os.path.join(modelDir, 'dlib')
    openfaceModelDir = os.path.join(modelDir, 'openface')

    dlibFacePredictor = os.path.join(dlibModelDir,
        "shape_predictor_68_face_landmarks.dat")
    networkModel = os.path.join(openfaceModelDir, 'nn4.small2.v1.t7')
    cuda = False

    align = openface.AlignDlib(dlibFacePredictor)
    net = openface.TorchNeuralNet(networkModel, imgDim=IMG_DIM, cuda=cuda)

    run()
