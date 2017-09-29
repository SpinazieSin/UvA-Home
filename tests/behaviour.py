import time

class BehaviourTest:
    def __init__(self, main):
        self._main = main

    def test(self):
        self._main.posture.resume()
        self._main.awareness.resume()

        self._main.speech.say("{} Hey there!", animations=[0])
        while(True):
            time.sleep(5)

