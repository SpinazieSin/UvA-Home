import argparse
import alproxy
import time
import sys

from behaviour.posture import Posture
from interaction.speech import Speech

# Global variables #
DEFAULT_IP = "pepper.local"
DEFAULT_PORT = 9559

class Main:
    def __init__(self):
        self.ALProxy = alproxy.ALProxy(
                "tcp://{}:9559".format(args.ip if args.ip else DEFAULT_IP))
        self.posture = Posture(self.ALProxy.app.session)
        self.speech = Speech(self.ALProxy.app.session)

    def main(self, args):
        self.ALProxy.test_all()

    def shutdown(self):
        self.posture.sleep()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='UvA-Home 2018.')

    # Optional arguments
    parser.add_argument("--testbehaviour", help="Starts the tests for the behaviour class.",
                        action="store_true")
    parser.add_argument("--nosleep", help="Don't set the robot to sleep mode after termination.",
                        action="store_true")
    parser.add_argument("--ip", help="NAOqi's IP, defaults to pepper.local.")


    args = parser.parse_args()

    try:
        main = Main()

        if args.testbehaviour:
            main.posture.resume()
            main.speech.say("{} Hey there!", animations=[0])
            while(True):
                time.sleep(5)
        else:
            main.main(args)
            print("Done...")

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        if not args.nosleep:
            main.shutdown()
        sys.exit(0)
