class Posture:

    # sets the volume to a default value
    def __init__(self, session):
        self.posture = session.service("ALRobotPosture")
        self.motion = session.service("ALMotion")
        self.basic_awareness = session.service("ALBasicAwareness")

    def resume(self):
        print("Posture on")
        self.motion.wakeUp()
        self.posture.goToPosture("Stand", 1.0)

    def stop(self):
        print("Posture off")
        self.motion.rest()
