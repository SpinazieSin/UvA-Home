# -*- encoding: UTF-8 -*-
# Get an image from NAO. Display it and save it using PIL.

import sys
import time

# Python Image Library
import Image
from naoqi import ALProxy
import cv2
from scipy import misc
from scipy import ndimage
import numpy as np
import math
from random import randint
import matplotlib.pyplot as plt
# from timeout import timeout
import timeout_decorator
import argparse
import glob
dresolution = 1    # QVGA
dcolorSpace = 0   # kDepthColorSpace
plt.ion()

# def show_blobs(IP, PORT, usedataset, dataset, show_images, iterations):
#     """
#     First get an image from Nao, then show it on the screen with PIL.
#     """
#
#     if not usedataset:
#         almemory = ALProxy("ALMemory", "pepper.local", 9559)
#         camProxy = ALProxy("ALVideoDevice", IP, PORT)
#         camProxy.setActiveCamera(2)
#         videoClient = camProxy.subscribe("python_client", dresolution, dcolorSpace, 5)
#     try:
#         trials_per_bin = 1
#         gridsize = (21,8)
#         ydistance = 320/gridsize[0]
#         xdistance = 240/gridsize[1]
#
#         startpoints = []
#         for i in range(gridsize[0] + 1):
#             for j in range(gridsize[1] + 1):
#                 samplex = (xdistance * j) + 1
#                 sampley = (ydistance * i) + 1
#                 if samplex == 0:
#                     samplex += 3
#
#                 if sampley == 0:
#                     sampley += 3
#
#                 if samplex > 240:
#                     samplex -= 4
#
#                 if sampley > 320:
#                     sampley -= 4
#
#                 startpoints.append((samplex, sampley))
#
#         if show_images:
#             plt.ion()
#
#         if usedataset:
#             filenames = glob.glob(dataset + "singletest/3D/*.png")
#             loopcount = len(glob.glob(dataset + "singletest/3D/*.png"))
#             print("found " + str(loopcount) + " files.")
#         else:
#             loopcount = iterations
#
#         for i in range(loopcount):
#             starttime = time.time()
#             if usedataset:
#                 # print(str(filenames[i]))
#                 loadtimea = time.time()
#                 image = np.array(cv2.imread(str(filenames[i]), 0))
#                 loadtimeb = time.time()
#                 # print("time to load image: " + str(loadtimeb - loadtimea))
#                 starttime = time.time()
#                 annotated_image, _ = annotate(image, startpoints, True, 5)
#                 endtime = time.time()
#                 print("time for single cycle:" + str(endtime - starttime))
#
#                 if show_images:
#                     plt.imshow(annotated_image, cmap="gray")
#                     plt.draw()
#                 time.sleep(10)
#             else:
#                 print("taking image!")
#                 naoImage = camProxy.getImageRemote(videoClient)
#                 imageWidth = naoImage[0]
#                 imageHeight = naoImage[1]
#
#                 imageStr = naoImage[6]
#                 image = np.array([ord(x) for x in imageStr])
#                 image = image.reshape([240,320])
#                 annotated_image, _ = annotate(image, startpoints, True, 15)
#
#                 if show_images:
#                     plt.imshow(annotated_image, cmap="gray")
#                     plt.draw()
#
#     except KeyboardInterrupt:
#         if not usedataset:
#             camProxy.unsubscribe(videoClient)
#         print("exiting...")
#         sys.exit(0)
#
#     camProxy.unsubscribe(videoClient)
    # segProxy.unsubscribe("python_client")


def annotate_single3D(camProxy, gridsize=(17,8), threshold=5):
    camProxy.setActiveCamera(2)
    videoClient = camProxy.subscribe("python_client", dresolution, dcolorSpace, 5)
    gridsize = (17,8)
    ydistance = 320/gridsize[0]
    xdistance = 240/gridsize[1]

    startpoints = []
    for i in range(gridsize[0] + 1):
        for j in range(gridsize[1] + 1):
            samplex = (xdistance * j) + 1
            sampley = (ydistance * i) + 1
            if samplex == 0:
                samplex += 3

            if sampley == 0:
                sampley += 3

            if samplex > 240:
                samplex -= 4

            if sampley > 320:
                sampley -= 4

            startpoints.append((samplex, sampley))

    # print("taking image!")
    naoImage = camProxy.getImageRemote(videoClient)
    imageWidth = naoImage[0]
    imageHeight = naoImage[1]

    imageStr = naoImage[6]
    image = np.array([ord(x) for x in imageStr])
    image = image.reshape([240,320])

    centroids, list_of_indices = annotate(image, startpoints, False, threshold)
    camProxy.unsubscribe(videoClient)
    return centroids, list_of_indices


def annotate_singleImage(image, gridsize=(17,8), threshold=5):
    gridsize = (17,8)
    ydistance = 320/gridsize[0]
    xdistance = 240/gridsize[1]

    startpoints = []
    for i in range(gridsize[0] + 1):
        for j in range(gridsize[1] + 1):
            samplex = (xdistance * j) + 1
            sampley = (ydistance * i) + 1
            if samplex == 0:
                samplex += 3

            if sampley == 0:
                sampley += 3

            if samplex > 240:
                samplex -= 4

            if sampley > 320:
                sampley -= 4

            startpoints.append((samplex, sampley))

    centroids, list_of_indices = annotate(image, startpoints, False, threshold)


    # for centr in centroids:
    #     draw_cross_long(image, centr, 255, centr[2])
    # plt.imshow(image, cmap="gray")
    # plt.draw()

    return centroids, list_of_indices


def annotate(image, startpoints, return_image, threshold):
    centroids = []
    filledpoints = set()
    clusterIndexList = []
    for startpoint in startpoints:
        # debug grid
        # draw_cross(image, startpoint, 255)
        if startpoint in filledpoints:
            continue
        tima = time.time()
        imagy = np.copy(image)
        list_of_indices = []

        try:
            filltime = time.time()
            if imagy[startpoint[0]][startpoint[1]] > 10:
                list_of_indices = fill(imagy, startpoint, 255, threshold)
                filledpoints.update(list_of_indices)
            # print("filltime: " + str(time.time() - filltime))
        except:
            pass

        # only get blobs of appropriate size
        if len(list_of_indices) < 200:
            continue

        # else:
        #     list_of_indices = np.array(list_of_indices)

        timb = time.time()
        # print("time for 1 fill: " + str(timb - tima))

        centroid = centeroidnp(np.array(list_of_indices))

        indicestoremove = []
        for i in range(len(list_of_indices)):
            if list_of_indices[i][1] > (centroid[1] + centroid[2][1] * 2.0):
                indicestoremove.append(i)
            elif list_of_indices[i][1] < (centroid[1] - centroid[2][1] * 2.0):
                indicestoremove.append(i)

        for index in sorted(indicestoremove, reverse=True):
            del list_of_indices[index]

        # only get blobs with high vertical standard deviation
        if centroid[2][0] > centroid[2][1]:
            centroids.append(centroid)
            clusterIndexList.append(np.array(list_of_indices))

    # if return_image:
    # for centr in centroids:
    #     draw_cross_long(image, centr, 255, centr[2])
    # plt.imshow(image, cmap="gray")
    # plt.draw()
        # return image
    # else:
    return centroids, clusterIndexList

def draw_cross(image, centr, fillcolor):
    # try:
    image[centr[0] +1][centr[1]] = fillcolor
    image[centr[0] +2][centr[1]] = fillcolor
    image[centr[0]][centr[1] + 1] = fillcolor
    image[centr[0]][centr[1] + 2] = fillcolor

    image[centr[0] -1][centr[1]] = fillcolor
    image[centr[0] -2][centr[1]] = fillcolor
    image[centr[0]][centr[1] - 1] = fillcolor
    image[centr[0]][centr[1] - 2] = fillcolor
    # except:
    #     pass
    # return image


def draw_cross_long(image, centr, fillcolor, stdd):
    # print("drawing long")
    # print("range:" + str(range(stdd[0])))
    try:
        for i in range(stdd[0]):
            image[centr[0] + i][centr[1]] = fillcolor
    except:
        pass
    try:
        for i in range(stdd[1]):
            image[centr[0]][centr[1] + i] = fillcolor
    except:
        pass
    try:
        for i in range(stdd[0]):
            image[centr[0] -i][centr[1]] = fillcolor
    except:
        pass
    try:
        for i in range(stdd[1]):
            image[centr[0]][centr[1] - i] = fillcolor
    except:
        pass


def centeroidnp(arr):
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    max_x = np.max(arr[:, 0])
    max_y = np.max(arr[:, 1])
    min_x = np.min(arr[:, 0])
    min_y = np.min(arr[:, 1])
    stdd = std(arr)
    return [sum_x/length, sum_y/length, stdd, (min_x,min_y),(max_x,max_y)]


def std(arr):
    xdev = np.std(arr[:, 0])
    ydev = np.std(arr[:, 1])
    return int(xdev), int(ydev)

# @timeout_decorator.timeout(0.05, timeout_exception=StopIteration)
def fill(data, start_coords, fill_value, threshold):
    """
    Flood fill algorithm

    Parameters
    ----------
    data : (M, N) ndarray of uint8 type
        Image with flood to be filled. Modified inplace.
    start_coords : tuple
        Length-2 tuple of ints defining (row, col) start coordinates.
    fill_value : int
        Value the flooded area will take after the fill.

    Returns
    -------
    None, ``data`` is modified inplace.
    """
    list_of_indices = [(start_coords[0], start_coords[1])]

    xsize, ysize = data.shape
    orig_value = data[start_coords[0], start_coords[1]]

    stack = set(((start_coords[0], start_coords[1]),))
    if fill_value == orig_value:
        # raise ValueError("Filling region with same value "
        #                  "already present is unsupported. "
        #                  "Did you already fill this region?")
        # print("already filled that!")
        return(np.array([]))

    # stepcounter terminates if the filling takes to long
    stepcounter = 0
    while stack:
        x, y = stack.pop()
        if abs(int(data[x, y]) - int(orig_value)) <= threshold:
            list_of_indices.append((x,y))
            stepcounter += 1
            if stepcounter > 3000:
                return list_of_indices

            data[x, y] = fill_value

            if x > 0:
                stack.add((x - 1, y))
            if x < (xsize - 1):
                stack.add((x + 1, y))
            if y > 0:
                stack.add((x, y - 1))
            if y < (ysize - 1):
                stack.add((x, y + 1))
    return list_of_indices


def get_annotated_image(IP, PORT, segProxy, camProxy, videoClient, almemory):
    """OLD METHOD, DO NOT USE."""
    segProxy = ALProxy("ALSegmentation3D", IP, PORT)
    segProxy.subscribe("python_client")
    segProxy.setBlobTrackingEnabled(1)
    rectangles = []
    # eh = segProxy.getBlobTrackingDistance()

    naoImage = camProxy.getImageRemote(videoClient)
    imageWidth = naoImage[0]
    imageHeight = naoImage[1]

    array = np.array(naoImage[6])
    naoqi_frame = Image.fromstring("RGB", (imageWidth, imageHeight), array)
    orig_img = np.array(naoqi_frame)

    ALVALUE = almemory.getData("Segmentation3D/BlobsList")
    # draw blobs in image
    for blob in ALVALUE[1]:
        [xangle, yangle] = blob[0]
        meandistance = blob[2]
        [realwidth, realheight] = blob[3]

        # get pixel coordinates
        xcoord = math.degrees(xangle) / 58 * imageWidth
        ycoord = math.degrees(yangle) / 45 * imageHeight

        # relocate pixels to new origin
        x = int(-xcoord + imageWidth/2)
        y = int(ycoord + imageHeight/2)

        # transform width and height data to pixel values
        ybound = meandistance * math.cos(math.radians(22.5))
        xbound = meandistance * math.cos(math.radians(29))
        maxysize = abs(ybound) * 2
        maxxsize = abs(xbound) * 2

        percentagewidth = realwidth / maxxsize * imageWidth
        percentageheight = realheight / maxysize * imageHeight
        halfpixwidth = int(percentagewidth/2)
        halfpixheight = int(percentageheight/2)

        # draw rectangles
        x1 = x - halfpixwidth
        y1 = y - halfpixheight
        x2 = x + halfpixwidth
        y2 = y + halfpixheight
        rect = [(x1, y1), (x2, y2)]
        rectangles.append(rect)
        cv2.rectangle(orig_img, (x1, y1), (x2, y2), (255,0,0), 2)
    return rectangles, orig_img


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--usedataset', default=True, type=bool)
    parser.add_argument('--dataset', default="./lab_dataset/")
    parser.add_argument('--IP', default="pepper.local")
    parser.add_argument('--PORT', default=9559)
    parser.add_argument('--show_images', default=True, type=bool)
    parser.add_argument('--iterations', default=100)
    args = parser.parse_args()

    show_blobs(args.IP, args.PORT, args.usedataset, args.dataset, args.show_images, args.iterations)
