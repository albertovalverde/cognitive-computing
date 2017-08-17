from naoqi import ALProxy
from PIL import Image
import time,  sys, pprint

class Robot:
    def __init__(self, IP, PORT, config, robotCheck):
        # type: (object, object, object, object) -> object
        pp = pprint.PrettyPrinter(indent=4)
        self.IP = IP
        self.PORT = PORT
        self.config = config
        self.robotCheck = robotCheck
        self.previousUtterance = ''

        # Dictionary of non-Watson functions that Naomi can perform
        # function for NLC
        self.robotFunctionsDict = Robot.__dict__
        self.robotFunctionsDict["DoFacialRecognition"] = Robot.__dict__["takeAPicture"] # Set the facial recognition command to take a picture
        self.robotFunctionsDict["DoVisualRecognition"] = Robot.__dict__["takeAPicture"] # Set the visual recognition command to take a picture
        self.robotFunctionsDict["DoTextRecognition"] = Robot.__dict__["takeAPicture"] # Set the text recognition command to take a picture
        self.robotFunctionsDict["DoCarRecognition"] = Robot.__dict__["takeAPicture"] # Set the custom visual recognition command to take a picture

        #function for conversation
        self.robotFunctionsDict["play-game-vision-1"] = Robot.__dict__["playGame"]  # Set the custom visual recognition command to take a picture

        if self.robotCheck:
            # # Initialise communication proxies for Naomi
            self.tts = ALProxy("ALTextToSpeech", IP, PORT) # Speech proxy
            self.ttsa = ALProxy("ALAnimatedSpeech", IP, PORT) # Animated speech proxy
            self.posture = ALProxy("ALRobotPosture", IP, PORT) # Posture proxy
            self.managerProxy = ALProxy("ALBehaviorManager", IP, PORT) # Behaviour manager proxy
            self.camProxy = ALProxy("ALVideoDevice", IP, PORT) # Camera proxy
            self.audioPlayer = ALProxy("ALAudioPlayer", IP, PORT) # Audio player proxy
            self.motion = ALProxy("ALMotion", IP, PORT) # Motion proxy
            self.battery = ALProxy("ALBattery", IP, PORT) # Battery proxy
            self.leds = ALProxy("ALLeds", IP, PORT) # Leds proxy (controls eye, chest, feet and head led colours)
            self.autonomousMovement = ALProxy("ALAutonomousMoves", IP, PORT) # Background movement controller proxy

            # Set variables to desired values
            self.audioFileId = self.audioPlayer.loadFile(self.config["audioFile1"]) # Location of audio file to play when asked to play a song
            self.leds.fadeRGB("FaceLeds", self.config["listeningColour"], 0) # Set eye colour
            self.motion.setFallManagerEnabled(self.config["fallManager"]) # Fall manager (look up in Aldebaran documentation for details)
            self.tts.setParameter("speed", int(self.config["speechSpeed"])) # Voice speed
            self.resolution = 2    # VGA
            self.colorSpace = 11   # RGB
    # ~--- Start the robot up with the default settings if it is connected ---~#
    def StartUp(self):
        if self.robotCheck:
            # Set starting parameters for Naomi
           # self.WakeUp() # wake it up
            #self.StandUp() # make Naomi stand up if not already standing
            self.leds.fadeRGB("FaceLeds", self.config["listeningColour"], 0) # set eye colour to listeningColour (set in config file)
            self.autonomousMovement.setBackgroundStrategy("backToNeutral") # turn on humanoid 'swaying'
    # define the robot functions
    def DoNothing(self): # Empty function, placeholder for when no robot function has been called in response to a user request
        pass
    def BatteryLevel(self): # Tell me Naomi's current battery charge
        self.printAndSay("My battery is at " + str(self.battery.getBatteryCharge()) + " per cent.")
    def StandUp(self): # Tell Naomi to stand up
        self.posture.goToPosture("Stand", self.config["standSpeed"])
    def SitDown(self): # Tell Naomi to sit down
        self.posture.goToPosture("Sit", self.config["sitSpeed"])
    def LieDownBelly(self): # Tell Naomi to lie down on its belly
        self.posture.goToPosture("LyingBelly", self.config["lieSpeed"])
        time.sleep(1)
        self.NoticeLyingAndStand()
    def LieDown(self): # Tell Naomi to lie down on its back
        self.posture.goToPosture("LyingBack", self.config["lieSpeed"])
        time.sleep(1)
        self.NoticeLyingAndStand()
    def Crouch(self): # Have Naomi crouch down (will automatically go back into standing mode once crouch is complete)
        self.posture.goToPosture("Crouch", self.config["crouchSpeed"])
    def RestSleep(self): # Put Naomi into rest mode
        self.motion.rest()
    def WakeUp(self): # Take Naomi out of rest mode
        self.motion.wakeUp()
        self.autonomousMovement.setExpressiveListeningEnabled(False)
    def PlayASong(self): # Make Naomi play some music that has been stored in its hard drive
        self.audioPlayer.play(self.audioFileId)
    # def Dance(self): # Make Naomi do the Gangnam Style dance
    #     print "dance started"
    #     self.leds.post.randomEyes(14)
    #     self.ttsa.post.say("^run(gangnam)")
    #     self.ledsForGangnam()
    #     self.leds.post.fadeRGB("ChestLeds", "white", 0.05)
    #     self.leds.post.fadeRGB("FeetLeds", "white", 0.05)
    #     self.leds.post.fadeRGB("FeetLeds", "blue", 0.05)
    #     self.printAndSay("Thank you! What a great audience")
    def Dance(self): # Make Naomi do the Thriller dance
        print "dance started"
        self.ttsa.post.say("^run(thriller)")
        self.leds.post.fadeRGB("ChestLeds", "white", 0.05)
        self.leds.post.fadeRGB("FeetLeds", "white", 0.05)
        self.leds.post.fadeRGB("FeetLeds", "blue", 0.05)
        self.printAndSay("Thank you! What a great audience")
    def ledsForGangnam(self): # "Light show" for the Gangnam Style dance
        fadeTiming = 0.05
        ledTiming = 0.2
        time.sleep(3)
        for i in range(1,14):
            self.leds.post.fadeRGB("BrainLeds", "green", fadeTiming)
            self.leds.post.fadeRGB("RightFootLeds", "red", fadeTiming)
            self.leds.fadeRGB("LeftFootLeds", "blue", fadeTiming)
            self.leds.fadeRGB("ChestLeds", "white", fadeTiming)
            time.sleep(ledTiming)
            self.leds.post.fadeRGB("BrainLeds", "blue", fadeTiming)
            self.leds.post.fadeRGB("RightFootLeds", "white", fadeTiming)
            self.leds.fadeRGB("LeftFootLeds", "red", fadeTiming)
            self.leds.fadeRGB("ChestLeds", "blue", fadeTiming)
            time.sleep(ledTiming)
            self.leds.post.fadeRGB("BrainLeds", "green", fadeTiming)
            self.leds.post.fadeRGB("RightFootLeds", "blue", fadeTiming)
            self.leds.fadeRGB("LeftFootLeds", "white", fadeTiming)
            self.leds.fadeRGB("ChestLeds", "red", fadeTiming)
    def TakeStepForward(self): # Make Naomi move slightly forward
        self.motion.moveTo(0.025, 0, 0)
    def NoticeLyingAndStand(self): # Automatically stands Naomi up when it's lying on the floor
        time.sleep(3)
        self.audibleListen()
        self.printAndSay("Ok, time to get back up!")
        self.StandUp()
    def audibleListen(self): # A sound that is played when Naomi has finished listening
        self.audioPlayer.playSine(self.config["sineFreq2"], 20, 0, 0.03)
        # time.sleep(0.09) # self.config["sineDelay"]
        # self.audioPlayer.playSine(self.config["sineFreq1"], 20, 0, 0.03)
        # time.sleep(0.01)
    def audibleComprehension(self): # A sound that is played when Naomi has understood something
        self.audioPlayer.playSine(self.config["sineFreq1"], 20, 0, 0.03)
        # time.sleep(0.09) # self.config["sineDelay"]
        # self.audioPlayer.playSine(self.config["sineFreq2"], 20, 0, 0.03)
        # time.sleep(0.01)
    def startThinking(self): # Puts Naomi into "thinking" mode - where it is waiting for a response from Watson
        if self.robotCheck:
            self.leds.post.fadeRGB("FaceLeds", self.config["responseColour"], self.config["ledTiming"]*1.5)
            self.audibleListen()
    def playGame(self):
        print "INTO THE PLAY GAME OF ROBOTFUNCTIONS"
        #self.printAndSay("Now, Pay Attention! The player has to count the RED Robots that displaying on the screen, please keep your attention on the screen!")
        # create proxy on ALMemory for comunicate with webview
        memProxy = ALProxy("ALMemory", self.IP, self.PORT)
        # raise event. Data can be int, float, list, string
        memProxy.raiseEvent("PlayGame", "todo:color selection")
    def takeAPicture(self):
        print "take a picture"
        #First get an image from Nao, then show it on the screen with PIL.
        if self.robotCheck:
            self.autonomousMovement.setBackgroundStrategy("none")
            self.leds.fadeRGB("FaceLeds", self.config["lookingColour"], 0)

            videoClient = self.camProxy.subscribe("python_client", self.resolution, self.colorSpace, 5)
            print "video client"

            t0 = time.time()
            # Get a camera image.
            # image[6] contains the image data passed as an array of ASCII chars.
            naoImage = self.camProxy.getImageRemote(videoClient)
            t1 = time.time()

            # Time the image transfer.
            # print "Acquisition delay:", t1 - t0

            self.camProxy.unsubscribe(videoClient)

            # Now we work with the image returned and save it as a PNG  using ImageDraw
            # package.
            # Get the image size and pixel array.
            imageWidth = naoImage[0]
            imageHeight = naoImage[1]
            array = naoImage[6]

            # Create a PIL Image from our pixel array.
            im = Image.frombytes("RGB", (imageWidth, imageHeight), array)

            # Save the image.
            im.save("Resources/Visual Recognition/NaomiPictureCapture.png", "PNG")

            print "Naomi is asking Watson what the picture is..."
            self.leds.fadeRGB("FaceLeds", "green", 0)
            self.tts.say("Ok, let me ask Watson!")
            self.leds.fadeRGB("FaceLeds", "yellow", 0)
            self.autonomousMovement.setBackgroundStrategy("backToNeutral")
    def WhatDidYouSay(self):
        self.printAndSay(self.previousUtterance)
    def RobotFunctionDec(self, robotFunction):
        # Controls eye colour for robot functions, as well as executing the desired robot function
        if self.robotCheck:
            self.leds.fadeRGB("FaceLeds", self.config["actionPerformColour"], 0)
        self.robotFunctionsDict.get(robotFunction, Robot.DoNothing)(self)
        if self.robotCheck:
            self.leds.fadeRGB("FaceLeds", self.config["listeningColour"], 0)
            self.audibleComprehension()
    def printAndSay(self, phrase):
        print 'Luxilor:', phrase, "\n"
        if self.robotCheck: # Speak the response phrase, changing eye colour appropriately, playing comprehension noise, etc.
            #self.audibleComprehension()
            self.leds.post.fadeRGB("FaceLeds", self.config["speakingColour"], 0)

            # create proxy on ALMemory for comunicate with webview
            memProxy = ALProxy("ALMemory", self.IP, self.PORT)
            # raise event. Data can be int, float, list, string
            memProxy.raiseEvent("RobotSay", phrase)

            self.ttsa.say(str(phrase))
            self.leds.post.fadeRGB("FaceLeds", self.config["listeningColour"], self.config["ledTiming"])
            self.autonomousMovement.setBackgroundStrategy("backToNeutral")


