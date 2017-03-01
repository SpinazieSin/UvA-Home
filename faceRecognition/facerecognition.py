# -*-coding:utf-8-*-
"""facial recognition class file for the media understanding 2017 project.

File name: facerecognition.py
Author: Media Understanding 2017
Date created: 23/2/2017
Date last modified: 23/2/2017
Python Version: 3.4
"""

import cv2
import os
import pickle
import time
import numpy as np
from sklearn.mixture import GMM
import openface

np.set_printoptions(precision=2)

IMG_DIM = 96
WIDTH = 320
HEIGHT = 240
THRESHOLD = 0.65


def known_face():
    """Check for known face.

    Return True and name if a face is recognized after 10 seconds otherwise
    return False and ""
    """
    # this stuff was in the main so I put it here
    # fileDir = os.path.dirname(os.path.realpath(__file__))
    fileDir = os.path.join(os.path.dirname(__file__), '')
    modelDir = os.path.join(fileDir, 'models')
    dlibModelDir = os.path.join(modelDir, 'dlib')
    openfaceModelDir = os.path.join(modelDir, 'openface')

    dlibFacePredictor = os.path.join(dlibModelDir,
                                     "shape_predictor_68_face_landmarks.dat")
    networkModel = os.path.join(openfaceModelDir, 'nn4.small2.v1.t7')
    cuda = False

    align = openface.AlignDlib(dlibFacePredictor)
    net = openface.TorchNeuralNet(networkModel, imgDim=IMG_DIM, cuda=cuda)

    video_capture = cv2.VideoCapture(0)
    video_capture.set(3, WIDTH)
    video_capture.set(4, HEIGHT)
    start_time = time.time()
    confidenceList = []
    person_list = []
    while True:
        # if it takes longer than 10 seconds, stop and return False and ""
        if time.time() - start_time > 5:
            video_capture.release()
            cv2.destroyAllWindows()
            print("found no known person")
            return False, ""

        ret, frame = video_capture.read()
        persons, confidences = infer(frame, align, net)
        print(persons, confidences)
        for i, c in enumerate(confidences):
            if c <= THRESHOLD:  # 0.5 is kept as threshold for known face.
                persons[i] = "_unknown"
        # print "P: " + str(persons) + " C: " + str(confidences)

        try:
            # append with two floating point precision
            confidenceList.append('%.2f' % confidences[0])
            person_list.append(persons[0])
            # enforce length of 10 for test_persons
            if len(person_list) <= 10:
                continue
            # get the last 10 items of the confidenceList
            test_persons = person_list[-10:]
            test_confidences = confidenceList[-10:]
            # sorry for terribly ugly if statement
            if test_persons.count(test_persons[0]) >= len(test_persons)/2 and \
                    test_persons[0] != "_unknown":
                # 0.8 threshold for known faces
                # the code previously written recognizes a face above 0.5
                # confidence score, I think thats a bit low so I added a
                # 0.8 minimal score here.
                if all(i >= 0.65 for i in test_confidences):
                    print(test_confidences)
                    print("found 5 high confidence scores")
                    video_capture.release()
                    cv2.destroyAllWindows()
                    return True, test_persons[0]
        except:
            # If there is no face detected, confidences matrix will be empty.
            # We can simply ignore it.
            pass
        # Print the person name and conf value on the frame
        cv2.putText(frame, "P: {} C: {}".format(persons, confidences),
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1)
        cv2.imshow('', frame)
        # quit the program on the press of key 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # When everything is done, release the capture
    # this only runs when someone breaks the loop by pressin gq, don't know
    # if we should keep that...
    video_capture.release()
    cv2.destroyAllWindows()


def infer(img, align, net):
    """Do inference yo."""
    # i added this for 2.7 idk why it works
    ospath = os.path.join(os.path.dirname(__file__), '')
    fullpath = ospath + '/generated-embeddings/classifier.pkl'
    classifierModel = fullpath

    with open(classifierModel, 'r') as f:
        (le, clf) = pickle.load(f)  # le - label and clf - classifer

    reps = getRep(img, align, net)
    persons = []
    confidences = []
    for rep in reps:
        try:
            rep = rep.reshape(1, -1)
        except:
            # print "No Face detected"
            return (None, None)
        predictions = clf.predict_proba(rep).ravel()
        # print predictions
        maxI = np.argmax(predictions)
        # max2 = np.argsort(predictions)[-3:][::-1][1]
        persons.append(le.inverse_transform(maxI))
        # print str(le.inverse_transform(max2)) + ": "+str( predictions [max2])
        # ^ prints the second prediction
        confidences.append(predictions[maxI])
        # print("Predict {} with {:.2f} confidence.".format(person,confidence))
        if isinstance(clf, GMM):
            dist = np.linalg.norm(rep - clf.means_[maxI])
            print("  + Distance from the mean: {}".format(dist))
            pass
    return (persons, confidences)


def getRep(bgrImg, align, net):
    """I don't know what this does."""
    if bgrImg is None:
        raise Exception("Unable to load image/frame")

    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)

    # Get the largest face bounding box
    # bb = align.getLargestFaceBoundingBox(rgbImg) #Bounding box

    # Get all bounding boxes
    bb = align.getAllFaceBoundingBoxes(rgbImg)

    if bb is None:
        # raise Exception("Unable to find a face: {}".format(imgPath))
        return None

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


if __name__ == '__main__':
    fileDir = os.path.dirname(os.path.realpath(__file__))
    # fileDir = os.path.join(os.path.dirname(__file__), '../../users')
    modelDir = os.path.join(fileDir, 'models')
    dlibModelDir = os.path.join(modelDir, 'dlib')
    openfaceModelDir = os.path.join(modelDir, 'openface')

    dlibFacePredictor = os.path.join(dlibModelDir,
                                     "shape_predictor_68_face_landmarks.dat")
    networkModel = os.path.join(openfaceModelDir, 'nn4.small2.v1.t7')
    cuda = False

    align = openface.AlignDlib(dlibFacePredictor)
    net = openface.TorchNeuralNet(networkModel, imgDim=IMG_DIM, cuda=cuda)

    known_face()
