# Naoqi Imports #
import qi

# additional Imports
import math
import time
import sys

from behaviour.posture import Posture

# Global variables #
IP = "pepper.local"
PORT = 9559

app = qi.Application(url="tcp://pepper.local:9559")
app.start()
session = app.session
posture = Posture(session)

def main():
    while True:
        time.sleep(2)

# Use the main function
if __name__=='__main__':
    try:
        posture.resume()
        main()
    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        posture.sleep()
        sys.exit(0)
