import time
from naoqi import ALProxy

def move_head(headxpos, headypos, im_width, im_height, ip_addr, motionProxy):
    """INFINITE MAGIC NUMBERS INCOMING."""
    width = im_width
    height = im_height
    # make sure movement is not made too often
    # Yaw is turning , left is positive, right is negative.
    currentAngle = motionProxy.getAngles("HeadYaw", True)[0]
    # move head only when ball is surely spotted
    if headxpos < (width/2 - 5):
        pdiff = (width/2 - 5) - headxpos
        turn = 0.15 * pdiff/80
        speed = abs(0.6 * pdiff/50)
        if speed > 0.8:
            speed = 0.8
        if speed < 0.2:
            speed = 0.2
        if currentAngle < 1.95:
            motionProxy.setAngles("HeadYaw", currentAngle + turn, speed)
            print("LEFT")
    if headxpos > (width/2 + 5):
        pdiff = (width/2 + 5) - headxpos
        turn = abs(0.15 * pdiff/80)
        speed = abs(0.6 * pdiff/50)
        if speed > 0.8:
            speed = 0.8
        if speed < 0.2:
            speed = 0.2
        if currentAngle > -1.95:
            motionProxy.setAngles("HeadYaw", currentAngle - turn, speed)
            print("RIGHT")
    # moving head up and down
    currentAngle = motionProxy.getAngles("HeadPitch", True)[0]
    if headypos > (height/2 - 5):
        pdiff = (height/2 - 5) - headypos
        turn = abs(0.09 * pdiff/80)
        speed = abs(0.6 * pdiff/50)
        if speed > 0.8:
            speed = 0.8
        if speed < 0.2:
            speed = 0.2
        if currentAngle < 0.51:
            motionProxy.setAngles("HeadPitch", currentAngle + turn, speed)
            print("UP")
    if headypos < (height/2 + 5):
        pdiff = (height/2 - 5) - headypos
        turn = abs(0.09 * pdiff/80)
        speed = abs(0.6 * pdiff/50)
        if speed > 0.8:
            speed = 0.8
        if speed < 0.2:
            speed = 0.2
        if currentAngle > -0.65:
            motionProxy.setAngles("HeadPitch", currentAngle - turn, speed)
            print("DOWN")
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
