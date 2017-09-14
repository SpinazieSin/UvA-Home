import peopledetector as ppldet
from naoqi import ALProxy
from naoqi import ALBroker

def main():
    IP = "pepper.local"  # Replace here with your NaoQi's IP address.
    PORT = 9559

    camProxy = ALProxy("ALVideoDevice", IP, PORT)
    sess, H, args, x_in, pred_boxes, pred_confidences = ppldet.setup_network()
    detections = ppldet.detect_people(camProxy, sess, H, args, x_in, pred_boxes, pred_confidences)
    print(detections)

    detections = ppldet.detect_people(camProxy, sess, H, args, x_in, pred_boxes, pred_confidences)
    print(detections)

    detections = ppldet.detect_people(camProxy, sess, H, args, x_in, pred_boxes, pred_confidences)
    print(detections)


if __name__ == '__main__':
    main()
