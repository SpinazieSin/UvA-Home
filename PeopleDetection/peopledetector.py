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
detectionstack = []

def setup_network():
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
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())
    saver.restore(sess, args.weights)
    pred_annolist = al.AnnoList()
    return sess, H, args, x_in, pred_boxes, pred_confidences


def detect_people(camProxy, sess, H, args, x_in, pred_boxes, pred_confidences):
    timestamp_base = time.strftime("%d:%m:%Y")

    time_a = time.time()
    # get 2D image from nao: 118

    # descriptions for 2D camera
    resolution2d = 2    # VGA

    # resolution2d = 1    # 320 * 240
    colorSpace2d = 11   # RGB

    camProxy.setActiveCamera(0)
    videoClient = camProxy.subscribe("python_client", resolution2d, colorSpace2d, 5)
    naoImage = camProxy.getImageRemote(videoClient)
    camProxy.unsubscribe(videoClient)

    # get blobs from own method
    centroids, indexList = blobfinder.annotate_single3D(camProxy)

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

    # check if naoqi is unresponsive due to unclosed subscriptions
    if naoImage == None:
        print("please restart nao...")
        return []

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
    pred_anno.imageName = timestamp_base + "-" + ".png"

    # add CNN rectangles to image in green, accepted_rects are all accepted positives
    cnn_annotated_image, rects, accepted_cnn_rects = add_rectangles(H, [img], np_pred_confidences, np_pred_boxes,
                                    use_stitching=True, rnn_len=H['rnn_len'], min_conf=args.min_conf, tau=args.tau, show_suppressed=args.show_suppressed)

    # clean rectangles from cnn
    accepted_cnn_rects_clean = make_4point_rectangles(accepted_cnn_rects)

    detectionstack.insert(0, accepted_cnn_rects_clean)
    if len(detectionstack) > 3:
        detectionstack.pop()

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

            # draw blob indices and centroids
            if show_images:
                img[tmp1][tmp2] = (255,255,0)
                blobfinder.draw_cross_long(img, centroids[i], [255,0,0], centroids[i][2])


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
    if show_images:
        for rect in history_detections:
            cv2.rectangle(img, rect[0], rect[1], (255,255,0), 2)

    # draw all detections from CNN in purple
    if show_images:
        for rect in detectionstack[0]:
            cv2.rectangle(img, rect[0], rect[1], (255,0,255), 2)

    # combine history and current frame detections
    final_combined_detections = list(detectionstack[0])
    for detection in history_detections:
        final_combined_detections.append(detection)

    # draw final detections in green
    if show_images:
        for rect in final_combined_detections:
            cv2.rectangle(img, rect[0], rect[1], (0,255,0), 2)

    time_b = time.time()
    print("time expanded: " + str(time_b - time_a) + ", fps: " + str(1/(time_b - time_a)))

    imname = "testimage" + timestamp_base
    if show_images:
        cropped_img = Image.frombytes("RGB", (H["image_width"], H["image_height"]), img)
        b, g, r = cropped_img.split()
        cropped_img = Image.merge("RGB", (r, g, b))
        crop_img = np.array(cropped_img)

        cv2.imshow(imname, crop_img)
        cv2.waitKey(1)
    return final_combined_detections


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


if __name__ == '__main__':
    main()
