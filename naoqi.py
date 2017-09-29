import qi

class Naoqi:
    # url format is: "tcp://IP:PORT"
    def __init__(self, url="tcp://127.0.0.1:9559"):
        self.url = url
        self.app = qi.Application(url=url)
        self.app.start()
        self.session = self.app.session

    # Allows the robot to say text
    def TextToSpeech(self):
        return self.session.service("ALTextToSpeech")

    def AnimatedSpeech(self):
        return self.session.service("ALAnimatedSpeech")

    # Soundlocator is for locating sound
    def SoundLocalization(self):
        return locateSound.SoundLocatorModule("SoundLocator")

    # Videodevice is for taking images from the videostream
    def VideoDevice(self):
        return self.session.service("ALVideoDevice")

    # AudioRecorder is for sound recording
    def AudioRecorder(self):
        return self.session.service("ALAudioRecorder")

    # AudioDevice is for sound level registration
    def AudioDevice(self):
        return self.session.service("ALAudioDevice")

    # Navigation module
    def Navigation(self):
        return self.session.service("ALNavigation")

    # 
    def Motion(self):
        return self.session.service("ALMotion")
    
    #  
    def RobotPosture(self):
        return self.session.service("ALRobotPosture")

    #
    def Memory(self):
        return self.session.service("ALMemory")

    def BasicAwareness(self):
        return self.session.service("ALBasicAwareness")   

    def test_all(self):
        print("Testing All...")
        print("TextToSpeech...")
        self.TextToSpeech()
        print("AnimatedSpeech...")
        self.AnimatedSpeech()
        # print("SoundLocalization")
        # self.init_soundLocalization()
        print("VideoDevice...")
        self.VideoDevice()
        print("AudioRecorder...")
        self.AudioRecorder()
        print("AudioDevice...")
        self.AudioDevice()
        # print("Navigation...")
        # self.init_navigation()
        print("Motion...")
        self.Motion()
        print("RobotPosture...")
        self.RobotPosture()
        print("Localization...")
        # self.Localization()
        print("Memory...")
        self.Memory()

#proxy = ALProxy()
