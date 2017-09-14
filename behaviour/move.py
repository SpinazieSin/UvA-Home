class Move:

    # sets the volume to a default value
    def __init__(self, session):
        self.motion = session.service("ALMotion")

    def walkForward(self):
        self.motion.moveInit()
        self.motion.moveTo(0.5, 0, 0)
