#!/usr/bin/python3

import threading
import speech_recognition as sr
# import time

exitFlag = 0


class SpeechThread (threading.Thread):
    """HELLO THIS IS PATRICK."""

    def __init__(self, threadID, name):
        """Initializing speech thread."""
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        """Define run."""
        print ("Starting " + self.name)
        while True:
            listen_for_speech(self.name)


def listen_for_speech(threadName):
    """Listen."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    print("sending audio to google")
    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key,
        # use`r.recognize_google(audio,key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        print("Found text: " + r.recognize_google(audio))
        print ("Exiting " + threadName)
        threadName.exit()
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google \
               Speech Recognition service; {0}".format(e))


# Create new threads
thread1 = SpeechThread(1, "recognition_thread")
# thread2 = myThread(2, "Thread-2", 2000)

# Start new Threads
thread1.start()
# thread2.start()
thread1.join()
# thread2.join()
print ("Exiting Main Thread")
