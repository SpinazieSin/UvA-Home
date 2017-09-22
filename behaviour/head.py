import time
from math import radians

class HeadMotion:
    def move_head(self, headxpos, headypos, im_width, im_height, motion_proxy):
        width = im_width
        height = im_height
        dwidth = im_width/55.20
        dheight = im_height/44.30

        # get current angles of the head
        currentAngle = motion_proxy.getAngles("HeadYaw", True)[0]
        self.stiffness_on(motion_proxy)

        # MOVE HEAD LEFT
        if headxpos < (width/2 - 5):
            pdiff = abs((width/2 - 5) - headxpos)
            turn = radians(pdiff / dwidth)
            speed = self.calculate_speed(turn)
            if currentAngle < 1.95:
                motionProxy.setAngles("HeadYaw", currentAngle + turn, speed)

        # MOVE HEAD RIGHT
        if headxpos > (width/2 + 5):
            pdiff = abs((width/2 + 5) - headxpos)
            turn = radians(pdiff / dwidth)
            speed = self.calculate_speed(turn)
            if currentAngle > -1.95:
                motionProxy.setAngles("HeadYaw", currentAngle - turn, speed)

        # MOVE HEAD UP
        currentAngle = motionProxy.getAngles("HeadPitch", True)[0]
        if headypos > (height/2 - 5):
            pdiff = abs((height/2 - 5) - headypos)
            turn = radians(pdiff / dheight)
            speed = self.calculate_speed(turn)
            if currentAngle < 0.51:
                motionProxy.setAngles("HeadPitch", currentAngle + turn, speed)

        # MOVE HEAD DOWN
        if headypos < (height/2 + 5):
            pdiff = abs((height/2 - 5) - headypos)
            turn = radians(pdiff / dheight)
            speed = self.calculate_speed(turn)
            if currentAngle > -0.65:
                motionProxy.setAngles("HeadPitch", currentAngle - turn, speed)

    def reset_head(self, motion_proxy, speed=0.1, yaw=0.0, pitch=-0.6):
        motion_proxy.setAngles("HeadPitch", pitch, speed)
        motion_proxy.setAngles("HeadYaw", yaw, speed)

    # calculate the speed at which the head is moved
    def calculate_speed(self, turn):
        speed = abs(0.15 * turn*1.5)
        if speed > 0.15:
            speed = 0.15
        if speed < 0.1:
            speed = 0.1
        return speed

    # execute a move by turning the stifness on
    def stiffness_on(self, motion_proxy):
        # We use the "Body" name to signify the collection of all joints
        pNames = "Head"
        pStiffnessLists = 0.8
        pTimeLists = 1.0
        motion_proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)

    def stiffnessOff(self, motion_proxy):
        pNames = "Body"
        pStiffnessLists = 0.0
        pTimeLists = 1.0
        motion_proxy.stiffnessInterpolation(pNames, pStiffnessLists, pTimeLists)
