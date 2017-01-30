import cv2
import numpy as np
import vision_definitions
import time
from naoqi import ALProxy

def imageloopstuff():
    IP = "10.42.0.78"
    PORT = 9559

    # Create proxy to nao
    print "Creating ALVideoDevice proxy to ", IP
    camProxy = ALProxy("ALVideoDevice", IP, PORT)

    # Register a Generic Video Module
    resolution = vision_definitions.kQVGA
    colorSpace = vision_definitions.kRGBColorSpace
    fps = 30

    # create image
    width = 320
    height = 240
    image = np.zeros((height, width, 3), np.uint8)


    nameId = camProxy.subscribe("python_GVM", resolution, colorSpace, fps)
    print 'getting images in remote'

    counter = 0
    while True:
        nao_image = camProxy.getImageRemote(nameId)
        if nao_image is None:
            print "Cannot capture."
            if cv2.waitKey(120) & 0xFF == ord('q'):
                break
        elif nao_image[6] == None:
            print "no image data string."
        else:
            # translate value to mat
            values = map(ord, list(nao_image[6]))
            i = 0
            for y in range(0, height):
                for x in range(0, width):
                    image.itemset((y, x, 0), values[i + 0])  # H
                    image.itemset((y, x, 1), values[i + 1])  # S
                    image.itemset((y, x, 2), values[i + 2])  # V
                    i += 3
            print "updated image", type(image)
            # bgr_image = cv2.cvtColor(image, cv2.COLOR_YUV2BGR)
            # gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # RUN CLASSIFIER

            cv2.imshow('findContours', gray_image)
            cv2.imwrite("faces_sub_69/subject69_"+ str(counter) +".png", gray_image)
            if cv2.waitKey(120) & 0xFF == ord('q'):
                break
            counter += 1

    camProxy.unsubscribe(nameId)
    cv2.destroyAllWindows()


def face_detection_stuff():
    # Replace this with your robot's IP address
    IP = "10.42.0.78"
    PORT = 9559

    # Create a proxy to ALFaceDetection
    try:
      faceProxy = ALProxy("ALFaceDetection", IP, PORT)
    except Exception, e:
      print "Error when creating face detection proxy:"
      print str(e)
      exit(1)

    # Subscribe to the ALFaceDetection proxy
    # This means that the module will write in ALMemory with
    # the given period below
    period = 500
    faceProxy.subscribe("Test_Face", period, 0.0 )

    # ALMemory variable where the ALFaceDetection module
    # outputs its results.
    memValue = "FaceDetected"

    # Create a proxy to ALMemory
    try:
        memoryProxy = ALProxy("ALMemory", IP, PORT)
    except Exception, e:
      print "Error when creating memory proxy:"
      print str(e)
      exit(1)

    # A simple loop that reads the memValue and checks whether faces are detected.
    for i in range(0, 20):
        time.sleep(0.5)
        val = memoryProxy.getData(memValue, 0)
        print ""
        print "\*****"
        print ""

    # Check whether we got a valid output: a list with two fields.
    if(val and isinstance(val, list) and len(val) == 2):
        # We detected faces !
        # For each face, we can read its shape info and ID.
        # First Field = TimeStamp.
        timeStamp = val[0]
        # Second Field = array of face_Info's.
        faceInfoArray = val[1]

        try:
          # Browse the faceInfoArray to get info on each detected face.
            for faceInfo in faceInfoArray:
                # First Field = Shape info.
                faceShapeInfo = faceInfo[0]
                # Second Field = Extra info (empty for now).
                faceExtraInfo = faceInfo[1]
                print "  alpha %.3f - beta %.3f" % (faceShapeInfo[1], faceShapeInfo[2])
                print "  width %.3f - height %.3f" % (faceShapeInfo[3], faceShapeInfo[4])
        except Exception, e:
            print "faces detected, but it seems getData is invalid. ALValue ="
            print val
            print "Error msg %s" % (str(e))
    else:
        print "Error with getData. ALValue = %s" % (str(val))
        # Unsubscribe the module.

    faceProxy.unsubscribe("Test_Face")
    print "Test terminated successfully."


if __name__ == '__main__':
    # face_detection_stuff()
    imageloopstuff()
