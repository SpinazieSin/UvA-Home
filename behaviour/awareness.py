class Awareness:

    # sets the volume to a default value
    def __init__(self, naoqi):
        self.basic_awareness = naoqi.BasicAwareness()
        self.basic_awareness.setEngagementMode("FullyEngaged")

    def resume(self):
        print("FullyEngaged on")
        self.basic_awareness.startAwareness()

        print("Hello.")

    def stop(self):
        print("FullyEngaged off")
        self.basic_awareness.stopAwareness()
