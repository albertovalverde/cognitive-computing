# ~--- Import custom Python modules ---~#
import B1_csvFileReading
import B1_BarcodeReading
# ~--- Import required modules from NaoQi and Python ---~#
from naoqi import ALProxy
import time
import sys
import random
import subprocess
# ~--- Set proxies to access Naomi's modules ---~#

class PersonalityInsights:
    def __init__(self, IP, PORT, robotCheck):
        # ~--- Prepare Naomi for demo ---~#
        self.robotCheck = robotCheck
        if self.robotCheck:
            self.tts = ALProxy("ALTextToSpeech", IP, PORT)
            self.leds = ALProxy("ALLeds", IP, PORT)
            self.ttsa = ALProxy("ALAnimatedSpeech", IP, PORT)
            self.motion = ALProxy("ALMotion", IP, PORT)
            self.tts.setParameter("speed", 93) # set speech speed
        # ~--- Get the personality insights available ---~#
        PersonalityInsightsFile = "Personality Insights/PersonalityInsights.csv"
        csvReaderModule = B1_csvFileReading.CSVFileReading(PersonalityInsightsFile)
        self.PersonalityInsights = csvReaderModule.readPersonalityInsightsCSV()
        self.barcodeReaderModule = B1_BarcodeReading.BarcodeReading(IP, PORT, robotCheck)
        self.printClassCreationSuccess()
# ~--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---~#

    def printClassCreationSuccess(self):
        print "Personality insights class successfully initialised.\n"

    def PI_Request(self):
        # ~--- Read a person's barcode ---~#
        print "PI_Request successfully initiated."
        if self.robotCheck:
            self.leds.fadeRGB("FaceLeds", "green", 0)
            self.tts.say("Please preesent your Q R code.")
            self.leds.fadeRGB("FaceLeds", "magenta", 0)
            person = self.barcodeReaderModule.readBarcode()
        else:
            print "Type in a person's name for the personality insights demo:"
            person = raw_input()
        if person != 0:
            print "\nPerson is confirmed to be " + person + "\n"
            WatsonKnowsAboutYou = ["Let me ask Watson what he thinks of " + person, "I see that " + person + " has met Watson, this is what he thought!", "This is what Watson thinks about " + person + "!"]
            for i in range(len(self.PersonalityInsights)):
                if person in self.PersonalityInsights[i][0]:
                    personalityPortrait = self.PersonalityInsights[i][1]
                    if self.robotCheck:
                        self.leds.fadeRGB("FaceLeds", "green", 0)
                        self.ttsa.say(random.choice(WatsonKnowsAboutYou))
                    break
                else:
                    personalityPortrait = ("I couldn't find that person! I guess that " + person + " has " +
                    "not met Watson yet!\n")
            print "Your personality portrait, as determined by Watson, is as follows.\n"
            print personalityPortrait
            if person == "Arya Stark" or person == "Jon Snow" or person =="Tyrion Lannister":
                personSunburst = "C:\Users\IBM_ADMIN\Documents\Projects\P4 - ThinkForum\Resources\Personality Insights\Sunbursts\\" + person + ".png"
                subprocess.call([ personSunburst ], shell=True)
            time.sleep(0.25)
            if self.robotCheck:
                self.leds.post.fadeRGB("FaceLeds", "green", 0.3)
                self.ttsa.say(personalityPortrait)
        else:
            print "\nQR code was not scanned."
            if self.robotCheck:
                self.leds.fadeRGB("FaceLeds", "green", 0)
        # ~--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---~#
        # ~--- Find the person's personality portrait ---~#
    # ~--- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---~#
