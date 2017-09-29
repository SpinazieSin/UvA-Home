class Posture:

    # sets the volume to a default value
    def __init__(self, naoqi):
        self.posture = naoqi.RobotPosture()
        self.motion = naoqi.Motion()

    def resume(self):
        print("Posture on")
        self.motion.wakeUp()
        self.posture.goToPosture("Stand", 1.0)

    def stop(self):
        print("Posture off")
        self.motion.rest()
