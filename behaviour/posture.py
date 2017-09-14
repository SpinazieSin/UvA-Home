class Posture:

    # sets the volume to a default value
    def __init__(self, session):
        self.posture = session.service("ALRobotPosture")
        self.motion = session.service("ALMotion")
        self.basic_awareness = session.service("ALBasicAwareness")

    def resume(self):
        print("Waking up.")
        self.motion.wakeUp()
        self.basic_awareness.startAwareness()
        self.basic_awareness.setEngagementMode("FullyEngaged")
        print("Hello.")


    def sleep(self):
        print("Going to sleep")
        self.basic_awareness.stopAwareness()
        self.motion.rest()
        print("Goodnight")
