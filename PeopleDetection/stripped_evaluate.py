import tensorflow as tf
import os
import json
import subprocess
from scipy.misc import imread, imresize
import cv2
import Image
from scipy import misc
import numpy as np
import time
import math
import glob
import json
import matplotlib.pyplot as plt

from train import build_forward
from utils.annolist import AnnotationLib as al
from utils.train_utils import add_rectangles, rescale_boxes

import cv2
import sys
import argparse
import image3D_test as blobfinder
from naoqi import ALProxy
from naoqi import ALBroker
use_dataset = False
load_annotations = False

def get_results(args, H):
    tf.reset_default_graph()
    x_in = tf.placeholder(tf.float32, name='x_in', shape=[H['image_height'], H['image_width'], 3])
    print("placeholder made")

    # THE FIRST IF GETS CALLED
    if H['use_rezoom']:
        print("building forward")
        pred_boxes, pred_logits, pred_confidences, pred_confs_deltas, pred_boxes_deltas = build_forward(H, tf.expand_dims(x_in, 0), 'test', reuse=None)
        grid_area = H['grid_height'] * H['grid_width']
        pred_confidences = tf.reshape(tf.nn.softmax(tf.reshape(pred_confs_deltas, [grid_area * H['rnn_len'], 2])), [grid_area, H['rnn_len'], 2])
        if H['reregress']:
            pred_boxes = pred_boxes + pred_boxes_deltas
    else:
        pred_boxes, pred_logits, pred_confidences = build_forward(H, tf.expand_dims(x_in, 0), 'test', reuse=None)

    saver = tf.train.Saver()
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        saver.restore(sess, args.weights)
        pred_annolist = al.AnnoList()

        # Robot information
        IP = "pepper.local"  # Replace here with your NaoQi's IP address.
        PORT = 9559

        # proxy to 2D camera
        if not use_dataset:
            camProxy = ALProxy("ALVideoDevice", IP, PORT)
            camProxy.setActiveCamera(0)

        # proxy to 3D camera
        # depthCamProxy = ALProxy("ALVideoDevice", IP, PORT)
        # depthCamProxy.setActiveCamera(2)

        # proxy to 3D segmentation
        # segProxy = ALProxy("ALSegmentation3D", IP, PORT)
        # segProxy.subscribe("python_client")
        # segProxy.setBlobTrackingEnabled(1)
        # print("depth threshold: " + str(segProxy.getDeltaDepthThreshold()))

        # proxy to people detection

        # motionProxy = ALProxy("ALMotion", IP, PORT)

        # memory for retrieving blobs
        if not use_dataset:
            almemory = ALProxy("ALMemory", "pepper.local", 9559)

        # descriptions for 2D camera
        resolution2d = 2    # VGA
        # resolution2d = 1    # 320 * 240
        colorSpace2d = 11   # RGB
        # videoClient = camProxy.subscribe("python_client", resolution2d, colorSpace2d, 5)

        # resolution3d = 1    # VGA
        # colorSpace3d = 11   # RGB
        # depthClient = depthCamProxy.subscribe("python_client", resolution3d, colorSpace3d, 5)
        setname = "images_single_6m"

        IMAGE_FOLDER = "./lab_dataset/" + setname + "/"
        timestamp_base = time.strftime("%d:%m:%Y") + "-"
        ANNOTATION_FILE = "./lab_dataset/blob_data/" + timestamp_base + "annotations.idl"
        try:
            os.remove(ANNOTATION_FILE)
        except OSError:
            pass

        print("Starting time: " + timestamp_base)
        framecounter = 1
        loopcount = 0
        filenames2d = []
        filenames3d = []
        accuracyList = []
        recallList = []
        precisionList = []
        peopleCounter = 0
        try:
            # evaluate N frames
            # for i in range(100):
            if use_dataset:
                # print(IMAGE_FOLDER + "3D/*.png")
                filenames2d = glob.glob(IMAGE_FOLDER + "2D/*.png")
                # print(filenames2d)
                filenames3d = glob.glob(IMAGE_FOLDER + "3D/*.png")
                loopcount = len(glob.glob(IMAGE_FOLDER + "3D/*.png"))
                print("found " + str(loopcount) + " files.")
                filenames3d.sort()
                filenames2d.sort()
            counter = 0
            plt.ion()
            while True:
                if use_dataset:
                    if counter == loopcount:
                        break
                    print("image: " + str(filenames2d[counter]))
                    # print("3d image: " + str(filenames3d[counter]))

                time_a = time.time()
                # get 2D image from nao: 118

                if not use_dataset:
                    camProxy.setActiveCamera(0)
                    videoClient = camProxy.subscribe("python_client", resolution2d, colorSpace2d, 5)
                    naoImage = camProxy.getImageRemote(videoClient)
                    camProxy.unsubscribe(videoClient)
                else:
                    bgr_img = cv2.imread(str(filenames2d[counter]), cv2.IMREAD_COLOR)
                    b,g,r = cv2.split(bgr_img)
                    orig_img = np.array(cv2.merge([r,g,b]))
                    image3d = np.array(cv2.imread(str(filenames3d[counter]), 0))

                # get blobs from own method
                if not use_dataset:
                    centroids, indexList = blobfinder.annotate_single3D(camProxy)
                else:
                    centroids, indexList = blobfinder.annotate_singleImage(image3d)
                    if load_annotations:
                        with open(IMAGE_FOLDER + setname + ".json") as json_data:
                            jsondata = json.load(json_data)

                newcentroids = []

                # resize blobs
                # original size = 320 * 240
                transform_x = np.linspace(25,0, num=320)
                transform_y = np.linspace(0,32, num=240)
                for j in range(len(indexList)):
                    for i in range(len(indexList[j])):
                        newx = indexList[j][i][1] - transform_x[indexList[j][i][1]]
                        newtuple = (indexList[j][i][0], round(newx))
                        indexList[j][i] = newtuple

                for i in range(len(centroids)):
                    newx = centroids[i][1] - transform_x[centroids[i][1]]
                    centroids[i] = [centroids[i][0], int(round(newx)), centroids[i][2], centroids[i][3], centroids[i][4]]

                if not use_dataset:
                    # check if naoqi is unresponsive due to unclosed subscriptions
                    if naoImage == None:
                        print("please restart nao...")
                        break

                    # get data from image package received from naoqi
                    imageWidth = naoImage[0]
                    imageHeight = naoImage[1]
                    array = naoImage[6]

                    # transform into regular PIL image and then np array
                    naoqi_frame = Image.frombytes("RGB", (imageWidth, imageHeight), array)
                    orig_img = np.array(naoqi_frame)

                # resize image if needed
                img = imresize(orig_img, (H["image_height"], H["image_width"]), interp='cubic')

                feed = {x_in: img}

                # get predictions from CNN
                (np_pred_boxes, np_pred_confidences) = sess.run([pred_boxes, pred_confidences], feed_dict=feed)
                pred_anno = al.Annotation()
                pred_anno.imageName = IMAGE_FOLDER + timestamp_base + str(framecounter) + ".png"

                # get blob rectangles from naoqi
                # blobrectangles = get_blob_rectangles(almemory, imageWidth, imageHeight)

                # save all found blobs
                # save_blobs(ANNOTATION_FILE, framecounter, blobrectangles)

                # add CNN rectangles to image in green, accepted_rects are all accepted positives
                cnn_annotated_image, rects, accepted_cnn_rects = add_rectangles(H, [img], np_pred_confidences, np_pred_boxes,
                                                use_stitching=True, rnn_len=H['rnn_len'], min_conf=args.min_conf, tau=args.tau, show_suppressed=args.show_suppressed)

                # clean rectangles from cnn
                accepted_cnn_rects_clean = make_4point_rectangles(accepted_cnn_rects)

                # accepted_cnn_rects_clean_all = make_4point_rectangles(rects)

                img = cnn_annotated_image

                # find annotations for file and draw rectangle
                if load_annotations:
                    ground_truth = []
                    for i in range(len(jsondata)):
                        if jsondata[i]["filename"] == filenames2d[counter]:
                            annotationlist = jsondata[i]["annotations"]
                            for annotation in annotationlist:
                                x1 = int(annotation["x"])
                                x2 = int(annotation["x"]) + int(annotation["width"])
                                y1 = int(annotation["y"])
                                y2 = int(annotation["y"]) + int(annotation["height"])
                                ground_truth.append([x1, y1, x2, y2])
                                cv2.rectangle(img, (x1, y1), (x2, y2), (255,0,255))

                # evaluate
                if use_dataset:
                    recall, avg_accuracy, peopleDetected, precision = evalframe(ground_truth, accepted_cnn_rects_clean)

                    peopleCounter += peopleDetected
                    recallList.append(recall)
                    accuracyList.append(avg_accuracy)
                    precisionList.append(precision)

                # convert to new image size
                for i in range(len(centroids)):
                    tmp1 = int((float(centroids[i][1]) / 320) * 640)
                    tmp2 = int((float(centroids[i][0]) / 240) * 480)
                    centroids[i][1] = tmp1
                    centroids[i][0] = tmp2

                    centroids[i][2] = (centroids[i][2][0] * 2, centroids[i][2][1] * 2)
                    centroids[i][3] = (centroids[i][3][0] * 2, centroids[i][3][1] * 2)


                for i in range(len(centroids)):
                    # draw corresponding blob
                    max_x = 0
                    max_y = 0
                    min_x = 639
                    min_y = 479
                    for j in range(len(indexList[i])):
                        tmp2 = int((float(indexList[i][j][1]) / 320) * 640)
                        tmp1 = int((float(indexList[i][j][0]) / 240) * 480)
                        if tmp2 > 639:
                            tmp2 = 639
                        if tmp1 > 479:
                            tmp1 = 479
                        if tmp1 > max_x:
                            max_x = tmp1
                        if tmp1 < min_x:
                            min_x = tmp1
                        if tmp2 > max_y:
                            max_y = tmp2
                        if tmp2 < min_y:
                            min_y = tmp2
                        indexList[i][j] = (tmp1, tmp2)
                        # draw blob indices
                        # img[tmp1][tmp2] = (255,255,0)
                    # draw bounding box of blob
                    # cv2.rectangle(img, (min_y, min_x), (max_y, max_x), (255,255,0))
                    # draw additional stuff
                    # try:
                    #     blobfinder.draw_cross_long(img, centroids[i], [255,0,255], centroids[i][2])
                    #     # cv2.rectangle(img, (centr[3][1], centr[3][0]), (centr[4][1], centr[4][0]), (255,0,255), 2)
                    # except:
                    #     # python yo, excepts everywhere
                    #     pass

                # combine the detection methods
                # detections, overlapping_test_rects = combine_detections(blobrectangles, accepted_cnn_rects_clean)

                # draw all rects that overlap with something in purple
                # for rect in overlapping_test_rects:
                #     cv2.rectangle(cnn_annotated_image, rect[0], rect[1], (255,0,255), 2)

                # draw all cnn rects that overlap with blob rects in blue
                # for rect in detections:
                #     cv2.rectangle(img, rect[0], rect[1], (0,0,255), 2)

                time_b = time.time()
                print("time expanded: " + str(time_b - time_a) + ", fps: " + str(1/(time_b - time_a))  )

                # new_img = cnn_annotated_image

                # pred_anno.rects = rects
                # pred_anno = rescale_boxes((H["image_height"], H["image_width"]), pred_anno, orig_img.shape[0], orig_img.shape[1])
                # pred_annolist.append(pred_anno)

                imname = "testimage"
                framecounter += 1
                cropped_img = Image.frombytes("RGB", (H["image_width"], H["image_height"]), img)
                b, g, r = cropped_img.split()
                cropped_img = Image.merge("RGB", (r, g, b))
                crop_img = np.array(cropped_img)

                cv2.imshow(imname, crop_img)
                cv2.waitKey(1)
                counter += 1
                if use_dataset:
                    print("intermediate accuracy: " + str(np.mean(accuracyList)))
                    print("intermediate recall: " + str(np.mean(recallList)))
                    print("intermediate precision: " + str(np.mean(precisionList)))
        except KeyboardInterrupt:
            # if ctrl-c unsubscribe to proxies
            print("exiting...")
            if not use_dataset:
                camProxy.unsubscribe(videoClient)
                # segProxy.unsubscribe("python_client")
            # depthCamProxy.unsubscribe(depthClient)
            sys.exit(0)

        # if program ends naturally unsubscriebe
        if not use_dataset:
            camProxy.unsubscribe(videoClient)
            # segProxy.unsubscribe("python_client")
        # depthCamProxy.unsubscribe(depthClient)
    if use_dataset:
        print("======================================")
        print("frames processed: " + str(counter))
        print("people correctly detected: " + str(len(accuracyList)))
        print("total people detected: " + str(peopleCounter))
        print("final accuracy: " + str(np.mean(accuracyList)))
        print("final recall: " + str(np.mean(recallList)))
        print("final precision: " + str(np.mean(precisionList)))

    return pred_annolist

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', required=True)
    parser.add_argument('--expname', default='')
    # parser.add_argument('--test_boxes', required=True)
    parser.add_argument('--gpu', default=0)
    parser.add_argument('--logdir', default='output')
    parser.add_argument('--iou_threshold', default=0.5, type=float)
    parser.add_argument('--tau', default=0.25, type=float)
    parser.add_argument('--min_conf', default=0.2, type=float)
    parser.add_argument('--show_suppressed', default=False, type=bool)
    args = parser.parse_args()
    os.environ['CUDA_VISIBLE_DEVICES'] = str(args.gpu)
    hypes_file = '%s/hypes.json' % os.path.dirname(args.weights)
    with open(hypes_file, 'r') as f:
        H = json.load(f)
    expname = args.expname + '_' if args.expname else ''
    # pred_boxes = '%s.%s%s' % (args.weights, expname, os.path.basename(args.test_boxes))
    # true_boxes = '%s.gt_%s%s' % (args.weights, expname, os.path.basename(args.test_boxes))

    print("starting predictions")
    pred_annolist = get_results(args, H)
    print("done with predicting")


def combine_centers(centers):
    goodcenters = []
    for centr in centers:
        connected_centers = []
        centercopy = list(centers)
        # print(centercopy)
        for centr2 in centercopy:
            if not centr == centr2:
                dist = calculateDistance(centr[0], centr[1], centr2[0], centr2[1])
                if dist < (centr[2][0] + centr[2][1])/2:
                    connected_centers.append(centr)
                    centercopy.remove(centr2)
        if connected_centers:
            x_aver = sum([v[0] for v in connected_centers]) / float(len(connected_centers))
            y_aver = sum([v[1] for v in connected_centers]) / float(len(connected_centers))
            std_x_aver = sum([v[2][0] for v in connected_centers]) / float(len(connected_centers))
            std_y_aver = sum([v[2][1] for v in connected_centers]) / float(len(connected_centers))
            tmp = centr
            tmp[0] = int(x_aver)
            tmp[1] = int(y_aver)
            tmp[2] = (int(std_x_aver), int(std_y_aver))
            goodcenters.append(tmp)
        else:
            goodcenters.append(centr)
    return goodcenters


def calculateDistance(x1,y1,x2,y2):
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
     return dist


def get_blob_rectangles(almemory, imageWidth, imageHeight):
    # Get 3D blobs from naoqi
    blobdata = almemory.getData("Segmentation3D/BlobsList")

    blobrectangles = []
    # loop through all found blobs and transform to 2D pixel coordinates
    for blob in blobdata[1]:
        [xangle, yangle] = blob[0]
        meandistance = blob[2]
        [realwidth, realheight] = blob[3]

        # filter blobs using real world size estimate
        # if realheight > 3.0:
        #     continue
        # if realwidth > 2.0:
        #     continue

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

        # transform into new point format
        x1 = x - halfpixwidth
        y1 = y - halfpixheight
        x2 = x + halfpixwidth
        y2 = y + halfpixheight
        rect = [(x1, y1), (x2, y2), (xcoord, ycoord)]
        blobrectangles.append(rect)
    return blobrectangles


def save_blobs(ANNOTATION_FILE, framecounter, blobrectangles):
    with open(ANNOTATION_FILE, 'a') as outfile:
        outfile.write('"' + IMAGE_FOLDER + timestamp_base + str(framecounter) + ".png" + '"')
        if blobrectangles:
            outfile.write(": ")
            for i in range(len(blobrectangles)):
                outfile.write("(" + str(blobrectangles[i][0][0]) + ", " + str(blobrectangles[i][0][1]) + ", " + str(blobrectangles[i][1][0]) + ", " + str(blobrectangles[i][1][1]) + ")")
                if i < len(blobrectangles) -1:
                    outfile.write(", ")
                else:
                    outfile.write(";\n")
        else:
            outfile.write(";\n")

def make_4point_rectangles(accepted_cnn_rects):
    accepted_cnn_rects_clean = []
    for rect in accepted_cnn_rects:
        newx1 = int(rect.cx - rect.width/2.)
        newy1 = int(rect.cy - rect.height/2.)
        newx2 = int(rect.cx + rect.width/2.)
        newy2 = int(rect.cy + rect.height/2.)
        newrect = [(newx1, newy1), (newx2, newy2), (rect.cx, rect.cy)]
        accepted_cnn_rects_clean.append(newrect)
    return accepted_cnn_rects_clean


def get_overlapping(rectlist):
    return

def combine_detections(blobrectangles, accepted_cnn_rects_clean):
    finalrects = []
    overlapping_test_rects = []
    for rect3d in blobrectangles:
        x13d = int(rect3d[0][0])
        y13d = int(rect3d[0][1])
        x23d = int(rect3d[1][0])
        y23d = int(rect3d[1][1])
        overlapping_rects = []
        for rect2d in accepted_cnn_rects_clean:
            x12d = int(rect2d[0][0])
            x22d = int(rect2d[1][0])
            y12d = int(rect2d[0][1])
            y22d = int(rect2d[1][1])
            overlapping_rects = []
            # print(x12d, x23d, x22d, x13d)
            # print(y12d, y23d, y22d, x13d)
            if not (x12d > x23d or x13d > x22d):
            # if x13d < x22d and x23d > x12d:
                print("first passed")
                # this does not seem to work yet
                # if y13d > y22d and y23d < y12d:
                if not (y22d < y13d or y23d < y12d):
                    #
                    overlapping_rects.append(rect2d)
                    overlapping_test_rects.append(rect2d)
                    print("overlap!")
        straight_distances = []
        for rects2d in overlapping_rects:
            xcenter2d = int((int(rect2d[1][0]) - int(rect2d[0][0]))/2)
            ycenter2d = int((int(rect2d[1][1]) - int(rect2d[0][1]))/2)
            xcenter3d = int(rect3d[2][0])
            ycenter3d = int(rect3d[2][1])

            # calculate straight line distance between centres
            straight_distances.append(abs(math.hypot(xcenter3d - xcenter2d, ycenter3d - ycenter2d)))

        # if list is not empty
        if straight_distances:
            bestfitindex = straight_distances.index(max(straight_distances))
            finalrects.append(overlapping_rects[bestfitindex])
    return finalrects, overlapping_test_rects


def evalframe(ground_truth, boxes_b):
    # check if a detection overlaps with ground_truth
    results = []
    peopleDetected = 0
    recall = 1.0
    precision = 1.0
    avg_accuracy = 1.0
    correctRects = [0] * len(boxes_b)
    print(correctRects)
    if ground_truth:
        for true_rect in ground_truth:
            recognized = False
            max_accuracy = 0.0
            # a
            true_x1 = true_rect[0]
            true_y1 = true_rect[1]
            true_x2 = true_rect[2]
            true_y2 = true_rect[3]
            for i in range(len(boxes_b)):
                # b
                detect_x1 = boxes_b[i][0][0]
                detect_y1 = boxes_b[i][0][1]
                detect_x2 = boxes_b[i][1][0]
                detect_y2 = boxes_b[i][1][1]
            #     # if A.right < B.left OR A.left > B.right
            #     #     OR A.bottom < B.top OR A.top > B.bottom THEN RETURN 0
                if (true_x2 < detect_x1):
                    overlap = 0.0
                    # print("no overlap 1")
                elif (true_x1 > detect_x2) :
                    overlap = 0.0
                    # print("no overlap 2")
                elif (true_y1 > detect_y2):
                    overlap = 0.0
                    # print("no overlap 3")
                elif (true_y2 < detect_y1):
                    overlap = 0.0
                    # print("no overlap 4")
                else:

                    if true_x2 > detect_x2:
                        width = detect_x2 - true_x1
                    else:
                        width = true_x2 - detect_x1
                    if true_y1 > detect_y1:
                        height = detect_y2 - true_y1
                    else:
                        height = true_y2 - detect_y1
                    overlap =  width * height
                    # print("width: " + str(width))
                    # print("height: " + str(height))
                    # print("overlap:" + str(overlap))
                    ground_truth_width = true_x2 - true_x1
                    ground_truth_height = true_y2 - true_y1
                    ground_truth_size = ground_truth_width * ground_truth_height
                    # print("ground truth size: " + str(ground_truth_size))
                    if ground_truth_size > overlap:
                        accuracy = float(overlap) / float(ground_truth_size)
                    else:
                        accuracy = float(ground_truth_size) /float(overlap)
                    if accuracy > 0.5:
                        # if the rect was overlapping, set it to correct in the
                        # correctRects list
                        correctRects[i] = 1
                        # print("accuracy: " + str(accuracy))
                        recognized = True
                        if accuracy > max_accuracy:
                            max_accuracy = accuracy
            if recognized:
                results.append(max_accuracy)
                peopleDetected += 1
        recall = len(results) / float(len(ground_truth))
        if results:
            avg_accuracy = np.mean(results)
        if boxes_b:
            precision = correctRects.count(1) / len(boxes_b)
        # print("recall: " + str(recall))
        # print("average accuracy: " + str(avg_accuracy))
        # print("people detected: " + str(peopleDetected))
    return recall, avg_accuracy, peopleDetected, precision



def non_max_suppression_fast(boxes, overlapThresh):
   # if there are no boxes, return an empty list
   if len(boxes) == 0:
      return []

   # initialize the list of picked indexes
   pick = []

   # grab the coordinates of the bounding boxes
   x1 = boxes[:,0]
   y1 = boxes[:,1]
   x2 = boxes[:,2]
   y2 = boxes[:,3]

   # compute the area of the bounding boxes and sort the bounding
   # boxes by the bottom-right y-coordinate of the bounding box
   area = (x2 - x1 + 1) * (y2 - y1 + 1)
   idxs = np.argsort(y2)

   # keep looping while some indexes still remain in the indexes
   # list
   while len(idxs) > 0:
      # grab the last index in the indexes list and add the
      # index value to the list of picked indexes
      last = len(idxs) - 1
      i = idxs[last]
      pick.append(i)

      # find the largest (x, y) coordinates for the start of
      # the bounding box and the smallest (x, y) coordinates
      # for the end of the bounding box
      xx1 = np.maximum(x1[i], x1[idxs[:last]])
      yy1 = np.maximum(y1[i], y1[idxs[:last]])
      xx2 = np.minimum(x2[i], x2[idxs[:last]])
      yy2 = np.minimum(y2[i], y2[idxs[:last]])

      # compute the width and height of the bounding box
      w = np.maximum(0, xx2 - xx1 + 1)
      h = np.maximum(0, yy2 - yy1 + 1)

      # compute the ratio of overlap
      overlap = (w * h) / area[idxs[:last]]

      # delete all indexes from the index list that have
      idxs = np.delete(idxs, np.concatenate(([last],
         np.where(overlap > overlapThresh)[0])))

   # return only the bounding boxes that were picked using the
   # integer data type
   return boxes[pick].astype("int")


if __name__ == '__main__':
    main()
