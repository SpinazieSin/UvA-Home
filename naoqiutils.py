# -*-coding:utf-8-*-
"""File Containing functions to interact with the naoqi robot.

File name: naoqiutils.py
Author: Media Understanding 2017
Date created: 1/3/2017
Date last modified: 1/3/2017
Python Version: 2.7
"""

from naoqi import ALProxy
import vision_definitions
import PIL.Image as Image

IP = "mio.local"
PORT = 9559
import sys


def speak(phrase):
    # errors if not converted to ascii :(
    phrase = phrase.encode('ascii', 'ignore')
    tts = ALProxy("ALTextToSpeech", IP, PORT)
    tts.setVolume(0.3)
    tts.say(phrase)

def get_images(amount):
    camProxy = ALProxy("ALVideoDevice", IP, PORT)
    resolution = 2    # VGA
    colorSpace = 11  # RGB

    videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)

    # Get a camera image.
    # image[6] contains the image data passed as an array of ASCII chars.
    raw_im_list = []
    for i in range(amount):
        naoImage = camProxy.getImageRemote(videoClient)

        imageWidth = naoImage[0]
        imageHeight = naoImage[1]
        array = naoImage[6]
        # Create a PIL Image from our pixel array.
        raw_im_list.append((imageWidth, imageHeight, array))

    rgb_im_list = []
    for imageWidth, imageHeight, array in raw_im_list:
        im = Image.fromstring("RGB", (imageWidth, imageHeight), array)
        rgb_im_list.append(im)

    camProxy.unsubscribe(videoClient)
    return rgb_im_list

def get_image():
    camProxy = ALProxy("ALVideoDevice", IP, PORT)
    resolution = 2    # VGA
    colorSpace = 11  # RGB

    videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)

    # Get a camera image.
    # image[6] contains the image data passed as an array of ASCII chars.
    naoImage = camProxy.getImageRemote(videoClient)

    imageWidth = naoImage[0]
    imageHeight = naoImage[1]
    array = naoImage[6]
    camProxy.unsubscribe(videoClient)

    # Create a PIL Image from our pixel array.
    im = Image.fromstring("RGB", (imageWidth, imageHeight), array)
    return im

def play_sine(frequency):
    try:
        aup = ALProxy("ALAudioPlayer", IP, PORT)
    except Exception, e:
        print "Could not create proxy to ALAudioPlayer"
        print "Error was: ", e
        sys.exit(1)
    aup.playSine(frequency, 40, 0, 0.5)
