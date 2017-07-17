from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import sys
import time
import math

SoundLocator = None
memory = None
navigation = None


class SoundLocatorModule(ALModule):
    """ A simple module able to react
    to facedetection events

    """
    def __init__(self, name):
        ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        self.tts = ALProxy("ALTextToSpeech")
        self.soundFound = False # continuesly gets updated during runtime
        self.soundAngle = 0.0 # continuesly gets updated during runtime

        # Subscribe to the FaceDetected event:
        global memory
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("ALSoundLocalization/SoundLocated", "SoundLocator", "onSoundLocated")

    def onSoundLocated(self, *_args):
        """ This will be called each time a face is
        detected.

        """
        # Unsubscribe to the event when talking,
        # to avoid repetitions
        try:
            memory.unsubscribeToEvent("ALSoundLocalization/SoundLocated", "SoundLocator")
        except RuntimeError:
            pass

        # self.tts.say("heard you")
        # print(_args)
        soundLocation = memory.getData("ALSoundLocalization/SoundLocated")
        angles = soundLocation[1]
        # print("angle1(azimuth suspect): ", math.degrees(angles[0]))
        # print("angle2(elevation suspect): ", math.degrees(angles[1]))
        # print("angle3: ", math.degrees(angles[2]))
        # print("angle4(confidence suspect): ", angles[3])
        # print(soundLocation[1])
        azimuth = math.degrees(angles[0])
        if azimuth > 180:
            azimuth = azimuth - 360

        if azimuth < -180:
            azimuth = azimuth + 360
        self.soundAngle = azimuth
        self.soundFound = True
        # print("angle: " + str(azimuth))

        # Subscribe again to the event
        memory.subscribeToEvent("ALSoundLocalization/SoundLocated", "SoundLocator", "onSoundLocated")

    def reset_variables(self):
        self.soundFound = False
        # self.soundAngle = 0.0 # idk if this is necessary


def main():
    # almemory = ALProxy("ALMemory", "pepper.local", 9559)
    # soundProxy = ALProxy("ALSoundLocalization", "pepper.local", 9559)
    # soundProxy.subscribe("ALSoundLocalization/SoundLocated")
    # soundProxy.subscribe("SoundLocated")
    myBroker = ALBroker("myBroker",
        "0.0.0.0",   # listen to anyone
        0,           # find a free port and use it
        "pepper.local",         # parent broker IP
        9559)

    global SoundLocator
    SoundLocator = SoundLocatorModule("SoundLocator")
    try:
        while True:
            # print("-")
            # time.sleep(1)
            pass
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        myBroker.shutdown()
        sys.exit(0)


if __name__ == '__main__':
    main()
