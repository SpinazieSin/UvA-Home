#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use findFreeZone Method"""

import qi
import argparse
import sys
import almath
import math


def main(session):
    """
    This example uses the findFreeZone method.
    """
    # Get the services ALNavigation, ALMotion and ALRobotPosture.

    navigation_service = session.service("ALNavigation")
    motion_service = session.service("ALMotion")
    posture_service = session.service("ALRobotPosture")

    # Wake up robot
    motion_service.wakeUp()

    # Send robot to Stand Init
    posture_service.goToPosture("StandInit", 0.5)

    # Scanning the environement.
    navigation_service.startFreeZoneUpdate()
    ###########################################################################
    # Add here an animation with timelines and moves (less than 60 seconds).  #
    # For example :
    motion_service.moveTo(0.0, 0.0, 2.0 * math.pi)
    ###########################################################################
    desiredRadius = 0.6
    displacementConstraint = 0.5
    result = navigation_service.findFreeZone(desiredRadius, displacementConstraint)

    errorCode = result[0]
    if errorCode != 1:
        worldToCenterFreeZone = almath.Pose2D(result[2][0], result[2][1], 0.0)
        worldToRobot = almath.Pose2D(motion_service.getRobotPosition(True))
        robotToFreeZoneCenter = almath.pinv(worldToRobot) * worldToCenterFreeZone
        motion_service.moveTo(robotToFreeZoneCenter.x, robotToFreeZoneCenter.y, 0.0)
    else :
        print "Problem during the update of the free zone."


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="pepper.local",
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
