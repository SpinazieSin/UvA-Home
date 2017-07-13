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
import re
import sys
import argparse
import blobfinder
from naoqi import ALProxy
from naoqi import ALBroker
use_dataset = True
show_images = True
setname = "images_crowd_all"

def get_results(args, H):
    tf.reset_default_graph()
    x_in = tf.placeholder(tf.float32, name='x_in', shape=[H['image_height'], H['image_width'], 3])

    use_dataset = bool(args.use_dataset)
    show_images = bool(args.show_images)
    setname = args.setname
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

        # descriptions for 2D camera
        resolution2d = 2    # VGA

        # resolution2d = 1    # 320 * 240
        colorSpace2d = 11   # RGB

        IMAGE_FOLDER = "./lab_dataset/" + setname + "/"
        timestamp_base = time.strftime("%d:%m:%Y")

        print("Starting time: " + timestamp_base)
        framecounter = 1
        loopcount = 0

        # filenames
        filenames2d = []
        filenames3d = []

        # evaluation data
        accuracyList = []
        recallList = []
        precisionList = []
        peopleCounter = 0
        accuracyList3d = []
        recallList3d = []
        precisionList3d = []
        peopleCounter3d = 0
        accuracyListcomb = []
        recallListcomb = []
        precisionListcomb = []
        peopleCountercomb = 0

        try:
            # evaluate N frames
            if use_dataset:
                filenames2d = glob.glob(IMAGE_FOLDER + "2D/*.png")
                filenames3d = glob.glob(IMAGE_FOLDER + "3D/*.png")

                loopcount = len(glob.glob(IMAGE_FOLDER + "3D/*.png"))
                print("found " + str(loopcount) + " files.")
                filenames3d.sort(key=lambda var:[int(x) if x.isdigit() else x for x in re.findall(r'[^0-9]|[0-9]+', var)])
                filenames2d.sort(key=lambda var:[int(x) if x.isdigit() else x for x in re.findall(r'[^0-9]|[0-9]+', var)])
            counter = 0
            plt.ion()
            detectionstack = []
            while True:
                if use_dataset:
                    if counter == loopcount:
                        break
                    print("image: " + str(filenames2d[counter]))

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
                    if use_dataset:
                        with open(IMAGE_FOLDER + setname + ".json") as json_data:
                            jsondata = json.load(json_data)

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
                pred_anno.imageName = IMAGE_FOLDER + timestamp_base + "-" + str(framecounter) + ".png"

                # add CNN rectangles to image in green, accepted_rects are all accepted positives
                cnn_annotated_image, rects, accepted_cnn_rects = add_rectangles(H, [img], np_pred_confidences, np_pred_boxes,
                                                use_stitching=True, rnn_len=H['rnn_len'], min_conf=args.min_conf, tau=args.tau, show_suppressed=args.show_suppressed)

                # clean rectangles from cnn
                accepted_cnn_rects_clean = make_4point_rectangles(accepted_cnn_rects)

                detectionstack.insert(0, accepted_cnn_rects_clean)
                if len(detectionstack) > 3:
                    detectionstack.pop()

                # img = cnn_annotated_image

                if use_dataset:
                    # find annotations for file and draw rectangle
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
                                cv2.rectangle(img, (x1, y1), (x2, y2), (0,0,255), thickness=2)

                    # evaluate
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
                        # if show_images:
                        #     img[tmp1][tmp2] = (255,255,0)

                    # draw bounding box of blob
                    # cv2.rectangle(img, (min_y, min_x), (max_y, max_x), (255,255,0), thickness=3)
                    # draw additional stuff
                    # try:
                        # blobfinder.draw_cross_long(img, centroids[i], [255,0,0], centroids[i][2])
                        # y_center = centroids[i][0]
                        # x_center = centroids[i][1]
                        # ystd = centroids[i][2][0]
                        # xstd = centroids[i][2][1]
                        # print(x_center)
                        # print(y_center)
                        # print(ystd)
                        # print(xstd)
                        # cv2.rectangle(img, (x_center - xstd, y_center - ystd), (x_center + xstd, y_center + ystd), (255,0,255), 2, thickness=3)
                        # cv2.rectangle(img, (x_center - xstd, y_center - ystd), (x_center + xstd, y_center + ystd), (255,0,255), thickness=2)
                    # except:
                        # python yo, excepts everywhere
                        # pass

                if use_dataset:
                    # evaluate the 3D data
                    recall3d, avg_accuracy3d, peopleDetected3d, precision3d = evalframe3d(ground_truth, indexList)


                    peopleCounter3d += peopleDetected3d
                    recallList3d.append(recall3d)
                    accuracyList3d.append(avg_accuracy3d)
                    precisionList3d.append(precision3d)

                # find history detections
                history_detections = []
                for i in range(len(centroids)):
                    for frame in detectionstack:
                        for rect in frame:
                            true_x1 = rect[0][0]
                            true_y1 = rect[0][1]
                            true_x2 = rect[1][0]
                            true_y2 = rect[1][1]
                            insidecount = 0
                            for j in range(len(indexList[i])):
                                (y,x) = indexList[i][j]
                                if true_x1 < x < true_x2 and true_y1 < y < true_y2:
                                    # if point is in rectangle
                                    insidecount += 1

                            accuracy = float(insidecount) / float(len(indexList[i]))
                            if accuracy > 0.5:
                                # print("doint the thing")
                                firstset = (centroids[i][1] - ((true_x1 - true_x2)/2), rect[0][1])
                                secondset = (centroids[i][1] + ((true_x1 - true_x2)/2), rect[1][1])
                                history_detections.append([firstset, secondset, (rect[0][0] + (rect[1][0] - rect[0][0])/2, rect[0][1] + (rect[1][1] - rect[0][1])/2)])

                # draw all detections made from history
                # for rect in history_detections:
                #     cv2.rectangle(img, rect[0], rect[1], (255,0,255), 2)

                # draw all detections from CNN
                # for rect in detectionstack[0]:
                #     cv2.rectangle(img, rect[0], rect[1], (255,0,255), 2)

                # combine history and current frame detections
                final_combined_detections = list(detectionstack[0])
                for detection in history_detections:
                    final_combined_detections.append(detection)

                if use_dataset:
                    recallcomb, avg_accuracycomb, peopleDetectedcomb, precisioncomb = evalframe(ground_truth, final_combined_detections)
                    peopleCountercomb += peopleDetectedcomb
                    recallListcomb.append(recallcomb)
                    accuracyListcomb.append(avg_accuracycomb)
                    precisionListcomb.append(precisioncomb)


                for rect in final_combined_detections:
                    cv2.rectangle(img, rect[0], rect[1], (0,255,0), 2)

                time_b = time.time()
                print("time expanded: " + str(time_b - time_a) + ", fps: " + str(1/(time_b - time_a)))

                imname = "testimage" + timestamp_base
                framecounter += 1
                if show_images:
                    cropped_img = Image.frombytes("RGB", (H["image_width"], H["image_height"]), img)
                    b, g, r = cropped_img.split()
                    cropped_img = Image.merge("RGB", (r, g, b))
                    crop_img = np.array(cropped_img)

                    cv2.imshow(imname, crop_img)
                    cv2.waitKey(1)
                counter += 1
                if use_dataset:
                    print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
                    print("intermediate accuracy: " + str(np.mean(accuracyList)))
                    print("intermediate recall: " + str(np.mean(recallList)))
                    print("intermediate precision: " + str(np.mean(precisionList)))
                    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    print("intermediate 3d accuracy: " + str(np.mean(accuracyList3d)))
                    print("intermediate 3d recall: " + str(np.mean(recallList3d)))
                    print("intermediate 3d precision: " + str(np.mean(precisionList3d)))
                    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    print("intermediate comb accuracy: " + str(np.mean(accuracyListcomb)))
                    print("intermediate comb recall: " + str(np.mean(recallListcomb)))
                    print("intermediate comb precision: " + str(np.mean(precisionListcomb)))
        except KeyboardInterrupt:
            # if ctrl-c unsubscribe to proxies
            print("exiting...")
            if not use_dataset:
                camProxy.unsubscribe(videoClient)
            # depthCamProxy.unsubscribe(depthClient)
            sys.exit(1)

        # if program ends naturally unsubscriebe
        if not use_dataset:
            camProxy.unsubscribe(videoClient)
            segProxy.unsubscribe("python_client")
    if use_dataset:
        print("======================================")
        print("frames processed: " + str(counter))
        print("dataset: " + setname)
        print("network used: " + str(args.weights))
        print("total people detected: " + str(peopleCounter))
        print("final accuracy: " + str(np.mean(accuracyList)))
        print("final recall: " + str(np.mean(recallList)))
        print("final precision: " + str(np.mean(precisionList)))
        print("final 3d accuracy: " + str(np.mean(accuracyList3d)))
        print("final 3d recall: " + str(np.mean(recallList3d)))
        print("final 3d precision: " + str(np.mean(precisionList3d)))
        print("final comb accuracy: " + str(np.mean(accuracyListcomb)))
        print("final comb recall: " + str(np.mean(recallListcomb)))
        print("final comb precision: " + str(np.mean(precisionListcomb)))

    return pred_annolist

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', default="./trained_nets/combined_inception_60k/save.ckpt-40000")
    parser.add_argument('--expname', default='')
    parser.add_argument('--test_boxes', default="./data/TUD-Brussels/small/smallnotation.idl")
    parser.add_argument('--gpu', default=0)
    parser.add_argument('--logdir', default='output')
    parser.add_argument('--iou_threshold', default=0.5, type=float)
    parser.add_argument('--tau', default=0.25, type=float)
    parser.add_argument('--min_conf', default=0.2, type=float)
    parser.add_argument('--show_suppressed', default=False, type=bool)
    parser.add_argument('--use_dataset', default=0)
    parser.add_argument('--show_images', default=1)
    parser.add_argument('--setname', default="images_crowd_all")

    args = parser.parse_args()
    os.environ['CUDA_VISIBLE_DEVICES'] = str(args.gpu)
    hypes_file = '%s/hypes.json' % os.path.dirname(args.weights)
    with open(hypes_file, 'r') as f:
        H = json.load(f)
    expname = args.expname + '_' if args.expname else ''
    pred_boxes = '%s.%s%s' % (args.weights, expname, os.path.basename(args.test_boxes))
    true_boxes = '%s.gt_%s%s' % (args.weights, expname, os.path.basename(args.test_boxes))

    print("starting predictions")
    pred_annolist = get_results(args, H)
    print("done with predicting")


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


def evalframe3d(ground_truth, indexList):
    # check if a detection overlaps with ground_truth
    results = []
    peopleDetected = 0
    recall = 1.0
    precision = 1.0
    avg_accuracy = 1.0
    correctRects = [0] * len(indexList)
    # print(correctRects)
    if ground_truth:
        for true_rect in ground_truth:
            recognized = False
            max_accuracy = 0.0
            max_size = 0
            # a
            true_x1 = true_rect[0]
            true_y1 = true_rect[1]
            true_x2 = true_rect[2]
            true_y2 = true_rect[3]
            # loop over blobs
            # print("blobs: " + str(len(indexList)))
            for i in range(len(indexList)):
                # b
                insidecount = 0
                for j in range(len(indexList[i])):
                    (y,x) = indexList[i][j]
                    if true_x1 < x < true_x2 and true_y1 < y < true_y2:
                        # if point is in rectangle
                        insidecount += 1
                # print(insidecount)
                accuracy = float(insidecount) / float(len(indexList[i]))
                # at least 50% inside the bbox and take largest blob
                if accuracy > 0.5:
                    recognized = True
                    if len(indexList[i]) > max_size and accuracy > max_accuracy:
                        max_accuracy = accuracy
                        max_size = len(indexList[i])
                        correctRects[i] = 1
            if recognized:
                results.append(max_accuracy)
                peopleDetected += 1
        recall = float(len(results)) / float(len(ground_truth))
        if results:
            avg_accuracy = np.mean(results)
        # print("blobs: " + str(len(indexList)))
        if indexList:
            # print("counts: " + str(correctRects.count(1)))
            precision = correctRects.count(1) / float(len(indexList))
    return recall, avg_accuracy, peopleDetected, precision


def evalframe(ground_truth, boxes_b):
    # check if a detection overlaps with ground_truth
    results = []
    peopleDetected = 0
    recall = 1.0
    precisionList = []
    avg_accuracy = 1.0

    if ground_truth:
        print("ground truth boxes: " + str(len(ground_truth)))
        for true_rect in ground_truth:
            print("checking box")
            recognized = False
            max_accuracy = 0.0
            correctRects = 0
            true_x1 = true_rect[0]
            true_y1 = true_rect[1]
            true_x2 = true_rect[2]
            true_y2 = true_rect[3]
            for i in range(len(boxes_b)):
                detect_x1 = boxes_b[i][0][0]
                detect_y1 = boxes_b[i][0][1]
                detect_x2 = boxes_b[i][1][0]
                detect_y2 = boxes_b[i][1][1]
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

                    ground_truth_width = true_x2 - true_x1
                    ground_truth_height = true_y2 - true_y1
                    ground_truth_size = ground_truth_width * ground_truth_height

                    if ground_truth_size > overlap:
                        accuracy = float(overlap) / float(ground_truth_size)
                    else:
                        accuracy = float(ground_truth_size) /float(overlap)
                    if accuracy > 0.5:
                        # if the rect was overlapping, set it to correct in the
                        # correctRects list
                        correctRects += 1
                        # print("accuracy: " + str(accuracy))
                        recognized = True
                        if accuracy > max_accuracy:
                            max_accuracy = accuracy
            if boxes_b:
                print("precstuff")
                print(len(boxes_b))
                print(correctRects)
                print("precstuff end")
                precision = correctRects / float(len(boxes_b))
                precisionList.append(precision)

            if recognized:
                results.append(max_accuracy)
                peopleDetected += 1
        recall = len(results) / float(len(ground_truth))
        if results:
            avg_accuracy = np.mean(results)

        if precisionList:
            final_prec = np.mean(precisionList)
        # print("recall: " + str(recall))
        # print("average accuracy: " + str(avg_accuracy))
        # print("people detected: " + str(peopleDetected))
    return recall, avg_accuracy, peopleDetected, final_prec


if __name__ == '__main__':
    main()
