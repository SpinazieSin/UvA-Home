# Main file for detecting faces
# Thomas Groot

# Imports #
import vision_definitions
import numpy as np
import time
import sys
from math import floor
from PIL import Image
from cv2 import CascadeClassifier
from naoqi import ALProxy

# Local modules #
import tracking

# Global variables #
cascadePath = "haarcascade_frontalface_default.xml"

#############
# Functions #
#############

# Image container:
# image
# [0]: width.
# [1]: height.
# [2]: number of layers.
# [3]: ColorSpace.
# [4]: time stamp (seconds).
# [5]: time stamp (micro-seconds).
# [6]: binary array of size height * width * nblayers containing image data.
# [7]: camera ID (kTop=0, kBottom=1).
# [8]: left angle (radian).
# [9]: topAngle (radian).
# [10]: rightAngle (radian).
# [11]: bottomAngle (radian).
# Try to take an image

def collect_faces(video_service, motionProxy=None):
    print("Making face database...")
    # Create classifier
    faceCascade = CascadeClassifier(cascadePath)
    # predict_image_pil = Image.open('face.jpg').convert('L')
    # predict_image = np.array(predict_image_pil, 'uint8')
    # faces = faceCascade.detectMultiScale(predict_image)
    resolution = 2
    colorSpace = 11
    # Top camera
    cameraID = 0
    # Create video session
    video_client = video_service.subscribe("python_client", resolution, colorSpace, 5)
    # select camera
    video_service.setParam(vision_definitions.kCameraSelectID, cameraID)
    
    # A list of all recognized faces
    recognized_faces = []
    start_time = time.time()
    current_time = 0.0
    while current_time < 20.0:
        # Get image
        try:
            image = video_service.getImageRemote(video_client)
            if image == None:
                raise
        except:
            print("Failed image")
            continue
        # Get the image size and pixel array.subscribe
        imageWidth = image[0]
        imageHeight = image[1]
        array = image[6]
        image_string = str(bytearray(array))
        # Create a PIL Image from our pixel array.
        im = Image.frombytes("RGB", (imageWidth, imageHeight), image_string)
        predict_image_pil = im.convert("L")
        predict_image = np.array(predict_image_pil, "uint8")
        # Faces contains and array with the coordinates of recognized faces in the original image
        # The structure is: [[int int int int]] for one face
        faces = faceCascade.detectMultiScale(predict_image)
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                if w > 95 and w < 350:
                    recognized_faces.append(predict_image[y: y + h, x: x + w])
                    if floor(current_time)%2 == 0.0 and motionProxy != None and (x, y, w, h) != (0, 0, 0, 0):
                        tracking.track_face_with_head(x, y, w, h, imageWidth, imageHeight, motionProxy)
        current_time = time.time() - start_time
    
    # Close video session
    video_service.unsubscribe(video_client)

    return recognized_faces


# Take a single picture and attempt to detect faces
def detect_once(video_service):
    resolution = 2
    colorSpace = 11
    cameraID = 0
    faceCascade = CascadeClassifier(cascadePath)
    print("Detecting faces...")
    face_list = []
    video_client = video_service.subscribe("python_client", resolution, colorSpace, 5)
    try:
        image = video_service.getImageRemote(video_client)
        if image == None:
            raise
    except:
        print("Failed image")
        return []
    # Get the image size and pixel array.subscribe
    imageWidth = image[0]
    imageHeight = image[1]
    array = image[6]
    image_string = str(bytearray(array))
    # Create a PIL Image from our pixel array.
    im = Image.frombytes("RGB", (imageWidth, imageHeight), image_string)
    predict_image_pil = im.convert("L")
    predict_image = np.array(predict_image_pil, "uint8")
    # Faces contains and array with the coordinates of recognized faces in the original image
    # The structure is: [[int int int int]] for one face
    faces = faceCascade.detectMultiScale(predict_image)
    if len(faces) > 0:
        for (x, y, w, h) in faces:
            face_list.append([[x,y],[x+w,y+h]])
    video_service.unsubscribe(video_client)
    return face_list, predict_image