import time
from naoqi import ALProxy
from math import radians

def move_head(headxpos, headypos, im_width, im_height, ip_addr, motionProxy):
    """INFINITE MAGIC NUMBERS INCOMING."""
    width = im_width
    height = im_height
    # for yaw:
    # 640 = pixel width using kVGA
    # camera angle is 60.97
    # 1 degree = 10.49 pixel difference
    # for pitch:
    # 480 = pixel heigth using kVGA
    # angle is 47.64
    # 1 degree = 10.075 pixel diff
    # Yaw is turning , left is positive, right is negative.

    # get current angles of the head
    currentAngle = motionProxy.getAngles("HeadYaw", True)[0]
    # MOVE HEAD LEFT
    if headxpos < (width/2 - 5):
        pdiff = abs((width/2 - 5) - headxpos)
        turn = radians(pdiff / 10.49)
        speed = abs(0.6 * turn*2)
        if speed > 0.8:
            speed = 0.8
        if speed < 0.2:
            speed = 0.2
        if currentAngle < 1.95:
            motionProxy.setAngles("HeadYaw", currentAngle + turn, speed)

    # MOVE HEAD RIGHT
    if headxpos > (width/2 + 5):
        pdiff = abs((width/2 + 5) - headxpos)
        turn = radians(pdiff / 10.49)
        speed = abs(0.6 * turn*2)
        if speed > 0.8:
            speed = 0.8
        if speed < 0.2:
            speed = 0.2
        if currentAngle > -1.95:
            motionProxy.setAngles("HeadYaw", currentAngle - turn, speed)

    # MOVE HEAD UP
    currentAngle = motionProxy.getAngles("HeadPitch", True)[0]
    if headypos > (height/2 - 5):
        pdiff = abs((height/2 - 5) - headypos)
        turn = radians(pdiff / 10.075)
        speed = abs(0.6 * turn*2)
        if speed > 0.8:
            speed = 0.8
        if speed < 0.2:
            speed = 0.2
        if currentAngle < 0.51:
            motionProxy.setAngles("HeadPitch", currentAngle + turn, speed)

    # MOVE HEAD DOWN
    if headypos < (height/2 + 5):
        pdiff = abs((height/2 - 5) - headypos)
        turn = radians(pdiff / 10.075)
        speed = abs(0.6 * turn*2)
        if speed > 0.8:
            speed = 0.8
        if speed < 0.2:
            speed = 0.2
        if currentAngle > -0.65:
            motionProxy.setAngles("HeadPitch", currentAngle - turn, speed)

    StiffnessOn(motionProxy)
    motionProxy.stiffnessInterpolation("Head", 0.0, 0.5)
    motionProxy.stopMove()

def StiffnessOn(proxy):
    # We use the "Body" name to signify the collection of all joints
    pNames = "Head"
    pStiffnessLists = 1.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)

def stiffnessOff(proxy):
    pNames = "Body"
    pStiffnessLists = 0.0
    pTimeLists = 1.0
    proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)
# shut down Nao
