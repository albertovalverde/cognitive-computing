# -*- coding: utf-8 -*-
#################################################################
#   Copyright (C) 2017 Alberto Valverde. All rights reserved.
#
#	> File Name:        < main_essilor.py >
#	> Author:           < Alberto Valverde >
#	> Mail:             < albertovalverd@hotmail.com >
#	> Created Time:     < 2017/07/21 >
#	> Last Changed:
#	> Description:		...
#################################################################
import sys, argparse, threading, time, random, csv, simplejson, json, pickle, os, datetime
import speech_recognition as sr
# from naoqi import ALModule
# from naoqi import ALProxy
from naoqi import *
from watchdog.observers import Observer
from NLC import NLC, NLCClassifierAdmin
from Config import ConfigAdmin
from PersonalityInsights import A1_PersonalityInsights
from VisualRecognition import WatsonVisualRecognition
from PythonForNaomi import RobotFunctions, StartNaomi
from Naked.toolshed.shell import execute_js, muterun_js
from ftplib import FTP


# ~--- Initial startup stuff ---~#
robotCheck = StartNaomi.checkIfRobotIsConnected()  # Check if robot is connected
PORT = 9559  # Get Naomi's port
IP_global = StartNaomi.getIP(robotCheck)  # Get Naomi's IP address
ConfigAdmin.createConfigFile(
    "Config/Robot Configuration.txt")  # Update the configuration .pkl file in case config changes have been made
config = pickle.load(
    open('Config/configurationDictionary.pkl', 'rb'))  # Loads configuration .pkl file into a Python dictionary
credentials = json.load(open('Config/credentials.json'))  # Loads all Bluemix credentials
# NLCClassifierAdmin.ClassifierOrganiser().updateMasterSpreadsheet() # Make sure that all NLC classifier IDs are up to date
# print "File containing NLC classifier information successfully updated.\n"
## ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ##

# ~--- Define the Watson demos ---~#
watsonVisRec = WatsonVisualRecognition.VisRecHandler(credentials["region"][config["regionVr"]]["VisualRecognition"],
                                                     config)
HandleNlc = NLC.ResponseHandler(credentials["region"][config["regionNlc"]]["NLC"],
                                config)  # This handles the determination of response for each NLC classification.



class SpeechRecoModule(ALModule):
    """ A module to use speech recognition """

    def __init__(self, name):
        ALModule.__init__(self, name)
        try:
            #self.asr.pause(True)
            self.asr = ALProxy("ALSpeechRecognition")
            self.ftp = FTP(IP_global)
            self.ftp.login("nao", "nao")
        except Exception as e:
            self.asr = None
        self.memory = ALProxy("ALMemory")

    def onLoad(self):
        #self.asr.pause(True)

        self.CognitiveConnection = MyHandler(config)


        from threading import Lock
        self.bIsRunning = False
        self.mutex = Lock()
        self.hasPushed = False
        self.hasSubscribed = False
        self.BIND_PYTHON(self.getName(), "onWordRecognized")


    def onUnload(self):
        from threading import Lock
        self.mutex.acquire()
        try:
            if (self.bIsRunning):
                if (self.hasSubscribed):
                    self.memory.unsubscribeToEvent("WordRecognized", self.getName())
                if (self.hasPushed and self.asr):
                    self.asr.popContexts()
        except RuntimeError, e:
            self.mutex.release()
            raise e
        self.bIsRunning = False;
        self.mutex.release()
        #self.asr.pause(False)

    def onInput_onStart(self):

        from threading import Lock
        self.mutex.acquire()
        if (self.bIsRunning):
            self.mutex.release()
            return
        self.bIsRunning = True
        try:

            if self.asr:
                self.asr.setVisualExpression(True)
                self.asr.pushContexts()
            self.hasPushed = True
            if self.asr:
                self.asr.pause(True)
                self.asr.setVocabulary(['a'],False)
                self.memory.subscribeToEvent("WordRecognized", self.getName(), "onWordRecognized")
                self.hasSubscribed = True
                self.asr.pause(False)


                self.tts = ALProxy("ALTextToSpeech", IP_global, PORT)
                self.audio = ALProxy("ALAudioDevice", IP_global, PORT)
                self.record = ALProxy("ALAudioRecorder", IP_global, PORT)
                self.aup = ALProxy("ALAudioPlayer", IP_global, PORT)
                # # # ----------> recording <----------
                #print 'start recording...'
                self.record_path = '/home/nao/out.wav'
                self.record.stopMicrophonesRecording()
                self.record.startMicrophonesRecording(self.record_path, 'wav', 16000, (0, 0, 1, 0))

                # ----------> playing the recorded file <----------
                #fileID = aup.playFile(record_path, 0.7, 0)


        except RuntimeError, e:
            self.mutex.release()
            self.onUnload()
            raise e
        self.mutex.release()

    def onWordRecognized(self, key, value, message):
        self.onUnload()
        self.record.stopMicrophonesRecording()
        print 'record over'

        filename = 'out.wav'
        file = open(filename, 'wb')
        self.ftp.retrbinary('RETR %s' % filename, file.write)



        # CognitiveConnection = MyHandler(config, "hello.wav")

        self.CognitiveConnection.on_modified(filename)

        # if (len(value) > 1 and value[1] >= 0.5):
        #     print 'recognized the word :', value[0]
        # else:
        #     print 'unsifficient threshold'


def PersonalityInsights():
    personSunburst = PersonalityInsights.PI_Request()


def DoVisualRecognition():
    picture = watsonVisRec.identifyPicture("/Resources/Visual Recognition/" + config["pictureFileName"])
    response_phrase = "This could be a " + picture["top_classification"] + ". I am " + str(
        picture["top_confidence"]) + "% sure."
    print "Returned possibilities are:"
    if len(picture["all_classifications"]):
        for i in range(min(len(picture["all_classifications"]), config["vrNumToReturn"])):
            try:
                print " -> " + str(i + 1) + ": " + picture["all_classifications"][i]["type_hierarchy"] + "/" + \
                      picture["all_classifications"][i]["class"] + ", " + str(picture["all_classifications"][i]["score"] * 100) + "%"
            except:
                print picture
    else:
        print "None. This could be an error."
    return [response_phrase, picture["time_elapsed"]]


def DoTextRecognition():
    picture = watsonVisRec.recogniseText("/Resources/Visual Recognition/" + config["pictureFileName"])
    text = ', '.join(picture["text"])
    response_phrase = "The text in the picture is:\n" + text
    if text == '':
        response_phrase = "I can't read any text in this picture!"
    return [response_phrase, picture["time_elapsed"]]


def DoFacialRecognition():
    picture = watsonVisRec.recogniseFaces("/Resources/Visual Recognition/" + config["pictureFileName"])

    if picture["identity_recognised"]:
        response_phrase = 'This looks like ' + picture["identity"] + ". I am " + str(
            picture["identity_confidence"]) + "% sure."
    elif picture["person_recognised"]:
        response_phrase = 'This looks like a ' + picture["gender"] + ", who is between the ages of " + str(
            picture["age_min"]) + " and " + str(picture["age_max"])
    else:
        response_phrase = "I can't recognise a person in this picture!"
    return [response_phrase, picture["time_elapsed"]]


def DoCustomVisualRecognition():
    picture = watsonVisRec.identifyCustomClassifier("/Resources/Visual Recognition/" + config["pictureFileName"])
    response_phrase = "I think this is a " + picture["top_classification"] + ". I am " + str(
        picture["top_confidence"]) + "% sure."
    return [response_phrase, picture["time_elapsed"]]


def DoNothing():
    return [0, 0]


watsonFunctions = {  # dictionary of the Watson demos that Naomi can perform
    'DoNothing': DoNothing,
    'DoTextRecognition': DoTextRecognition,
    'DoVisualRecognition': DoVisualRecognition,
    'DoFacialRecognition': DoFacialRecognition,
    'DoCarRecognition': DoCustomVisualRecognition,
    'PersonalityInsights': PersonalityInsights
}


## ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ##

def getext(filename):  # Get the file extension from a file.
    return os.path.splitext(filename)[-1].lower()


def confirmReadyForStartUp():
    print "\nReady to get started!"


watsonFunctions = {  # dictionary of the Watson demos that Naomi can perform
    'DoNothing': DoNothing,
    'DoTextRecognition': DoTextRecognition,
    'DoVisualRecognition': DoVisualRecognition,
    'DoFacialRecognition': DoFacialRecognition,
    'DoCarRecognition': DoCustomVisualRecognition,
    'PersonalityInsights': PersonalityInsights
}


## ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ##

def getext(filename):  # Get the file extension from a file.
    return os.path.splitext(filename)[-1].lower()


def confirmReadyForStartUp():
    print "\nReady to get started!"


class MyHandler():
    def __init__(self, config):
        #threading.Thread.__init__(self)

        self.ListOfNlcClassifiers = json.load(
            open('Resources/NLC/ListOfNlcClassifiersManual.json', 'r'))  # load JSON with list of nlc classifiers
        self.nlcClassifierName = config["firstNlc"]  # The first NLC classifier to analyse text against
        self.nlcClassifierID = self.ListOfNlcClassifiers[
            self.nlcClassifierName]  # The first NLC classifier ID to analyse text against
        self.Naomi = RobotFunctions.Robot(IP_global, PORT, config,
                                          robotCheck)  # Initialise all robot functions in variable "Naomi"
        self.Naomi.StartUp()  # Get Naomi out of rest mode, stand it up, set eye colour, etc.
        #self.speechToPath = speech_path

        confirmReadyForStartUp()  # Print start-up message to let user know that everything has been started smoothly

    def on_deleted(self, event):
        pass  # Ignore file deletions from the transcripts folder

    def on_modified(self,filename):

        print filename


        with sr.WavFile(filename) as source:  # use "test.wav" as the audio source
            audio = r.record(source)

            # Speech recognition using Google Speech Recognition
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`

                if robotCheck:
                    transcript2 = r.recognize_google(audio)
                else:
                    transcript2 = StartNaomi.getTextFake()
                print "User Say: " + transcript2

                if transcript2 == 'stop':
                    sys.exit('Stop - Error!')



                #self.Naomi.startThinking()  # Prepare to wait for the Watson NLC response

                nlcClassification = HandleNlc.classifyText(transcript2, self.nlcClassifierName, self.nlcClassifierID)  # Retrieve NLC

                #print nlcClassification + "___" + self.nlcClassifierName
                nlcResponse = HandleNlc.returnResponse(self.nlcClassifierName,
                                                       nlcClassification)  # Retrieve correct response for the NLC classification

                self.Naomi.printAndSay(nlcResponse[0])  # Print and say (if the robot is connected) the verbal response
                self.nlcClassifierID = nlcResponse[1]  # Set the classifier ID to be used for the next NLC request
                self.nlcClassifierName = nlcResponse[2]  # Set the classifier name to be used for the next NLC request
                self.Naomi.RobotFunctionDec(nlcClassification)  # If user requested a robot function, execute that function

                watsonResponse = watsonFunctions.get(nlcClassification,
                                                     DoNothing)()  # If user requested a Watson function, execute that function
                if watsonResponse[0]:
                    self.Naomi.printAndSay(watsonResponse[0])
                    print "Time required for API call:", watsonResponse[1], "seconds"

                self.Naomi.previousUtterance = nlcResponse[
                    0]  # Hold the last thing Naomi said in a variable so that it can be repeated if required

            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                Start()
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

            Start()


    # def run(Self):
    #     print " event started"
    #     Self.on_modified()
    #     pass
    #
    # def stop(Self):
    #     pass



def main():
    # ----------> main ini <----------
    # examples of declarations
    # myclass = threading_class(robot_IP, 1, robot_PORT )
    # myclass2 = simple_class(robot_IP, robot_PORT)
    # myclass3 = threading_class(robot_IP, 2,  robot_PORT)

    try:
    # ----------> run threads <----------
    # sample run threads
    #     myclass.start()
    #     myclass3.start()


         global r;
         r = sr.Recognizer()

         if robotCheck:
             print "With Robot"
             broker = ALBroker("pythonBroker", "0.0.0.0", 0, IP_global, PORT)
             global pythonSpeechModule;
             pythonSpeechModule = SpeechRecoModule('pythonSpeechModule')
             # pythonSpeechModule.onLoad()
             # pythonSpeechModule.onInput_onStart()
             # time.sleep(20)
             # pythonSpeechModule.onUnload()
         else:
             print "Without Robot"
             CognitiveConnection = MyHandler(config)
             CognitiveConnection.on_modified("out.wav")

         Start()



    except KeyboardInterrupt:
    # catch error
    # example of stop threads
    #     myclass.stop()
    #     myclass2.stop()
    #     myclass3.stop()
        print "Interrupted by user, shutting down"
        sys.exit(0)

def Start():
    if robotCheck:
        pythonSpeechModule.onLoad()
        pythonSpeechModule.onInput_onStart()
        time.sleep(200)
        pythonSpeechModule.onUnload()
    else:
        print "Without Robot"
        CognitiveConnection = MyHandler(config)
        CognitiveConnection.on_modified("Hello.wav")



if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--ip", type=str, default="192.168.1.36", help="Robot ip address")
    # parser.add_argument("--port", type=int, default=9559, help="Robot port number")
    # args = parser.parse_args()
    # # ----------> main <----------
    # main(args.ip, args.port)
    main()
