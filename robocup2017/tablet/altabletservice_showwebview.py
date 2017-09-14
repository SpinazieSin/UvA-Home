#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use showWebview Method"""

import qi
import argparse
import sys
import time


def main(session):
    """
    This example uses the showWebview method.
    To Test ALTabletService, you need to run the script ON the robot.
    """
    # Get the service ALTabletService.

    try:
        tabletService = session.service("ALTabletService")
        print(1)
        # Ensure that the tablet wifi is enable
        tabletService.enableWifi()
        print(2)
        tabletService.configureWifi("wpa","p-athome-sspl-uva", "baa3cc3b")
        print(tabletService.getWifiStatus())
        tabletService.setBackgroundColor("#0066ff")
        # Display a web page on the tablet
        val1 = tabletService.showWebview("http://www.google.com")
        print("showwebview: " + str(val1))

        print(3)
        time.sleep(3)
        print(4)
        # Display a local web page located in boot-config/html folder
        # The ip of the robot from the tablet is 198.18.0.1
        # tabletService.showWebview("http://198.18.0.1/apps/boot-config/preloading_dialog.html")
        print(5)
        time.sleep(3)
        print(6)
        # Hide the web view
        # tabletService.hideWebview()
        print(7)
    except Exception, e:
        print "Error was: ", e


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)
