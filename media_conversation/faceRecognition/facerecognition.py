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
import numpy as np
from sklearn.mixture import GMM
import openface
import sys
from PIL import Image
from naoqi import ALProxy
dir_path = os.path.dirname(os.path.realpath(__file__))
up_dir = os.path.dirname(os.path.dirname(dir_path))

sys.path.append(up_dir)

# import naoqiutils
import headmotions

np.set_printoptions(precision=2)

IMG_DIM = 96
WIDTH = 320
HEIGHT = 240
THRESHOLD = 0.4
REQUIRED_TRIALS = 2
IP = "mio.local"  # change is another robot is used
PORT = 9559
camProxy = ALProxy("ALVideoDevice", IP, PORT)
motionProxy = ALProxy("ALMotion", IP, PORT)
resolution = 2    # VGA
colorSpace = 11  # RGB
videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)

# def fast_known_face(use_nao=True, timeout=True):
#     """Check for known face.
#
#     Return True and name if a face is recognized after 10 seconds otherwise
#     return False and ""
#     """
#     # this stuff was in the main so I put it here
#     # fileDir = os.path.dirname(os.path.realpath(__file__))
#     fileDir = os.path.join(os.path.dirname(__file__), '')
#     modelDir = os.path.join(fileDir, 'models')
#     dlibModelDir = os.path.join(modelDir, 'dlib')
#     openfaceModelDir = os.path.join(modelDir, 'openface')
#
#     dlibFacePredictor = os.path.join(dlibModelDir,
#                                      "shape_predictor_68_face_landmarks.dat")
#     networkModel = os.path.join(openfaceModelDir, 'nn4.small2.v1.t7')
#     cuda = False
#
#     align = openface.AlignDlib(dlibFacePredictor)
#     net = openface.TorchNeuralNet(networkModel, imgDim=IMG_DIM, cuda=cuda)
#
#     start_time = time.time()
#     confidenceList = []
#     person_list = []
#     while True:
#         # if it takes longer than 10 seconds, stop and return False and ""
#         if time.time() - start_time > 5 and timeout:
#             print("found no known person")
#             return False, ""
#
#         naoqi_frames = naoqiutils.get_images(5)
#         frames = []
#         for nframe in naoqi_frames:
#             frame = np.array(nframe)
#             frames.append(frame)
#             persons, confidences = infer(frame, align, net)
#             print("P: " + str(persons) + " C: " + str(confidences))
#
#             # append with two floating point precision
#             for i, c in enumerate(confidences):
#                 if c <= THRESHOLD:  # 0.5 is kept as threshold for known face.
#                     persons[i] = "_unknown"
#             try:
#                 person_list.append(persons[0])
#                 confidenceList.append('%.2f' % confidences[0])
#             except Exception as e:
#                 pass
#         print("Person List: " + str(person_list))
#         try:
#             last_persons = person_list[:-4]
#             most_common = max(set(last_persons), key=last_persons.count)
#             if most_common != "_unknown":
#                 return True, most_common
#         except Exception as e:
#             pass


def known_face(use_nao=True, timeout=True):
    """Check for known face.

    Return True and name if a face is recognized after 10 seconds otherwise
    return False, this method is also able to take images with regular webcams
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

    if use_nao:
        pass  # dont worry bout it yo
    else:
        video_capture = cv2.VideoCapture(0)
        video_capture.set(3, WIDTH)
        video_capture.set(4, HEIGHT)
    confidenceList = []
    person_list = []
    images_taken_count = 0
    while True:
        # if it takes longer than 10 images, stop and return False and ""
        if images_taken_count > 10 and timeout:
            if not use_nao:
                video_capture.release()
                cv2.destroyAllWindows()
                camProxy.unsubscribe(videoClient)
                headmotions.stiffnessOff()
            print("found no known person")
            return False, ""

        if use_nao:
            naoqi_frame = get_image()
            # naoqi_frame is an rgb image, I checked this.
            frame = np.array(naoqi_frame)
        else:
            # line for using with webcams
            ret, frame = video_capture.read()

        persons, confidences = infer(frame, align, net)
        for i, c in enumerate(confidences):
            if c <= THRESHOLD:  # threshold for known faces.
                persons[i] = "_unknown"
        print("P: " + str(persons) + " C: " + str(confidences))

        try:
            # append with two floating point precision
            confidenceList.append('%.2f' % confidences[0])
            person_list.append(persons[0])
            # uncomment if you want to run a few cycles before recognition

            # if len(person_list) <= 4:
            #     continue

            # only check for equal persons in the last 4 entries.
            test_persons = person_list[-4:]
            # test_confidences = confidenceList[-4:]
            # sorry for terribly ugly if statement
            # if the last person is recognised more than once in list
            if test_persons.count(test_persons[-1]) >= REQUIRED_TRIALS and \
                    test_persons[-1] != "_unknown":
                # 0.8 threshold for known faces
                # the code previously written recognizes a face above 0.5
                # confidence score, I think thats a bit low so I added a
                # 0.8 minimal score here.
                # if all(i >= 0.65 for i in test_confidences):
                #     print(test_confidences)
                print("Found " + str(REQUIRED_TRIALS) + " high confidences.")
                if not use_nao:
                    video_capture.release()
                    cv2.destroyAllWindows()
                    camProxy.unsubscribe(videoClient)
                    headmotions.stiffnessOff()
                return True, test_persons[-1]
        except:
            # If there is no face detected, confidences matrix will be empty.
            # We can simply ignore it.
            pass
        # Print the person name and conf value on the frame
        # cv2.putText(frame, "P: {} C: {}".format(persons, confidences),
        #             (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
        #             (255, 255, 255), 1)
        # cv2.imshow('', frame)
        # quit the program on the press of key 'q'
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        images_taken_count += 1
    # When everything is done, release the capture
    # this only runs when someone breaks the loop by pressin gq, don't know
    # if we should keep that...
    # video_capture.release()
    # cv2.destroyAllWindows()


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

    # rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_RGB2BGR)
    rgbImg = bgrImg

    # Get the largest face bounding box
    # bb = align.getLargestFaceBoundingBox(rgbImg) #Bounding box

    # Get all bounding boxes
    bb = align.getAllFaceBoundingBoxes(rgbImg)

    if bb is None:
        # raise Exception("Unable to find a face: {}".format(imgPath))
        return None
    if len(bb) > 0:
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

    # print(alignedFaces)
    if alignedFaces is None:
        raise Exception("Unable to align the frame")

    reps = []
    for alignedFace in alignedFaces:
        reps.append(net.forward(alignedFace))

    # print reps
    return reps


def get_image():
    # Get a camera image.
    # image[6] contains the image data passed as an array of ASCII chars.
    naoImage = camProxy.getImageRemote(videoClient)

    imageWidth = naoImage[0]
    imageHeight = naoImage[1]
    array = naoImage[6]

    im = Image.fromstring("RGB", (imageWidth, imageHeight), array)
    return im


if __name__ == '__main__':
    # just ignore this stuff it's here in case we need to change some code back
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
