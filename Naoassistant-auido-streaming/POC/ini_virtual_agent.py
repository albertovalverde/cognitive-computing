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
import time, pickle
import cognitive_services
from naoqi import *
from ftplib import FTP
from PythonForNaomi import RobotFunctions, StartNaomi
import json
from watson_developer_cloud import ConversationV1
import speech_recognition as sr

config = pickle.load(
    open('Config/configurationDictionary.pkl', 'rb'))  # Loads configuration .pkl file into a Python dictionary
credentials = json.load(open('Config/credentials.json'))  # Loads all Bluemix credentials
ID_conversation = credentials["region"][config["regionVr"]]["Conversation"]["ID"]
User_conversation =  credentials["region"][config["regionVr"]]["Conversation"]["username"]
Pass_conversation =  credentials["region"][config["regionVr"]]["Conversation"]["password"]
print "Region is", config["regionVr"]
print "User is", User_conversation
print "Password is", Pass_conversation
print "ID is", ID_conversation, "\n"

conversation = ConversationV1(
            username=User_conversation,
            password=Pass_conversation,
            version='2016-09-20')
        # # replace with your own workspace_id
workspace_id = ID_conversation
#print ID_conversation + " / " + User_conversation + " / " + Pass_conversation

# ~--- Initial startup stuff ---~#
robotCheck = StartNaomi.checkIfRobotIsConnected()  # Check if robot is connected
PORT = 9559  # Get Naomi's port
IP_global = StartNaomi.getIP(robotCheck)  # Get Naomi's IP address


class SpeechRecoModule(ALModule):
    """ A module to use speech recognition """
    def __init__(self, name):
        ALModule.__init__(self, name)
        try:
            self.asr = ALProxy("ALSpeechRecognition")
            self.ftp = FTP(IP_global)
            self.ftp.login("nao", "nao")
            self.memory = ALProxy("ALMemory")
            self.memory.subscribeToMicroEvent("myMicroEvent", "pythonSpeechModule", "message", "playGameEnd") # catch event from webview
            self.google = sr.Recognizer()  # google specch recognition
            self.Naomi = RobotFunctions.Robot(IP_global, PORT, config,
                                              robotCheck)  # Initialise all robot functions in variable "Naomi"
            # self.speechToPath = speech_path
            self.response = conversation.message(workspace_id=workspace_id,
                                                 message_input={'text': ''})
            print(json.dumps(self.response, indent=2))

            self.WebviewResponse = None # Initialise values for WebView games

            self.Naomi.StartUp()  # Get Naomi out of rest mode, stand it up, set eye colour, etc.
            self.Naomi.printAndSay(self.response["output"]["text"][0])  # Print and say (if the robot is connected) the verbal response

        except Exception as e:
            self.asr = None
            print Exception


    def onLoad(self):
        # Module for Cognitive Services
        self.CognitiveConnection = cognitive_services.CognitiveService(IP_global, PORT, robotCheck)
        from threading import Lock
        self.bIsRunning = False
        self.mutex = Lock()
        self.hasPushed = False
        self.hasSubscribed = False
        self.BIND_PYTHON(self.getName(), "onWordRecognized")
        self.tts = ALProxy("ALTextToSpeech", IP_global, PORT)
        self.audio = ALProxy("ALAudioDevice", IP_global, PORT)
        self.record = ALProxy("ALAudioRecorder", IP_global, PORT)
        self.aup = ALProxy("ALAudioPlayer", IP_global, PORT)
        self.record_path = '/home/nao/out.wav'

    def onUnload(self):
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
                # # # ----------> recording <----------
                # print 'start recording...'
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
        with sr.WavFile(filename) as source:  # use "test.wav" as the audio source
            audio = self.google.record(source)
            # Speech recognition using Google Speech Recognition
            try:
                SpeechPause = False
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                transcript = self.google.recognize_google(audio)
                print transcript
                self.response = conversation.message(workspace_id=workspace_id,
                                                     message_input={'text': transcript},context=self.response['context'])
                print(json.dumps(self.response, indent=2))

                Deserialize = DeserializeResponse(self.response)

                # if Deserialize.playgame == "on":
                #     print "DESERIALIZE: on"
                #     self.Naomi.RobotFunctionDec(Deserialize.classified)  # If user requested a robot function, execute that function
                #     #STOP the speechrecognition
                #     SpeechPause = True
                # else:
                #     print "DESERIALIZE: off"
                #     SpeechPause = False


                #TODO THIS IS FOR CATCH WEBVIEW RESPONSE NOT GOOD CODE AT ALL

                if Deserialize.playgame == "on":
                    print "Adding event in robotfunction"
                    self.Naomi.RobotFunctionDec(
                        Deserialize.classified)  # If user requested a robot function, execute that function
                    # STOP the speechrecognition
                    SpeechPause = True

                self.Naomi.StartUp()
                self.Naomi.printAndSay(
                    Deserialize.text)  # Print and say (if the robot is connected) the verbal response


                if Deserialize.playresponse == "on":
                    print "Check results from webview"
                    #check the response from the webview (is not always active)
                    if self.WebviewResponse is not None:
                        print self.WebviewResponse
                        if str(Deserialize.inputText) == str(self.WebviewResponse):
                            self.Naomi.StartUp()
                            self.Naomi.printAndSay(
                            "Wou, Congratulations! You are a champion!. " + str(
                            Deserialize.inputText) + " red Robots were displayed on the Screen")  # Print and say (if the robot is connected) the verbal response
                        else:
                            self.Naomi.StartUp()
                            self.Naomi.printAndSay("Sorry! You need to keep more attention to the vision game. " + str(
                            self.WebviewResponse) + " red robots were displayed on the screen")  # Print and say (if the robot is connected) the verbal response
                        self.WebviewResponse = None


                    #to rollback
                    # if self.WebviewResponse is None:
                    #     print self.WebviewResponse
                    # if self.WebviewResponse is not None:
                    #     print self.WebviewResponse
                    #     if str(Deserialize.inputText) == str(self.WebviewResponse):
                    #         self.Naomi.StartUp()
                    #         self.Naomi.printAndSay(
                    #         "WOU, Congratulations! You are a champion!." + str(
                    #         Deserialize.inputText) + " red Robots were displayed in the Screen")  # Print and say (if the robot is connected) the verbal response
                    #     else:
                    #         self.Naomi.StartUp()
                    #         self.Naomi.printAndSay("Ohhh, Sorry! You need to keep mor attention." + str(
                    #         self.WebviewResponse) + " red robots were displayed on the screen")  # Print and say (if the robot is connected) the verbal response
                    #     self.WebviewResponse = None


            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")

            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

            if not SpeechPause:
               #Restart the iteration bucle
               StartIteration()



    # Call when finish the webview-game iteration
    def playGameEnd(self, strVarName, value, message):
        """callback when WebView trigger"""
        self.WebviewResponse = value
        print "Count of webview= " + str(value)
        self.Naomi.StartUp()
        self.Naomi.printAndSay("Well, Can you say me how many red robots was displaying on the screen?")  # Print and say (if the robot is connected) the verbal response
        StartIteration()

class Filteresponse:
    text = ""
    classified = ""
    playgame = ""
    playresponse=""
    intents = ""
    inputText = ""

def DeserializeResponse(response):

    print(json.dumps(response, indent=2))

    deserialize= Filteresponse
    try:
        deserialize.text = response["output"]["text"][0]
        print "text : " + deserialize.text
    except:
        deserialize.text = None
    try:
        deserialize.intents = response["intents"][0]["intent"]
        print "intents : " + deserialize.intents
    except:
        deserialize.intents = None
    try:
        deserialize.classified = response["output"]["nodes_visited"][len(response["output"]["nodes_visited"])-1]
        print "classified : " + deserialize.classified
    except:
        deserialize.classified = None
    try:
        deserialize.playgame = response["context"]["play_game"]
        print "play_game : " + deserialize.playgame
    except:
        deserialize.playgame = None
    try:
        deserialize.playresponse = response["context"]["play_response"]
        print "playresponse : " + deserialize.playresponse
    except:
        deserialize.playresponse = None
    try:
        deserialize.inputText = response["input"]["text"]
        print "input text : " + deserialize.inputText
    except:
        deserialize.inputText = None

    return deserialize



def StartIteration():
    if robotCheck:
        pythonSpeechModule.onLoad()
        pythonSpeechModule.onInput_onStart()
        time.sleep(400)
        pythonSpeechModule.onUnload()
    else:

        try:
            with open('response.json') as data_file:
                    data = json.load(data_file)
            response = data
        except:
            response = None

        stringToSay = StartNaomi.getTextFake()

        response = conversation.message(workspace_id=workspace_id,
                                                  message_input={'text': stringToSay}, context=response['context'])

        Deserialize = DeserializeResponse(response)
        #to review
        if Deserialize.playgame == "on":
            print "Adding event in robotfunction"
        if Deserialize.playresponse == "on":
            print "Check results from webview"
        # end to review

        with open('response.json', 'w') as outfile:
            json.dump(response, outfile)

        StartIteration()

def confirmReadyForStartUp():
    print "\nReady to get started!"
# This function is for testing in a NO robot mode "without robot"
# Say first hello bot and save the response in a local file "response.json"
# Important to pass between the conversation
def TestConversation():
    # try to delete old data in local path
    import os
    try:
        os.remove("response.json")
        print "deleting response.json for restart the process"
    except:
        print "no response.json to delete"
    response = conversation.message(workspace_id=workspace_id,
                                    message_input={'text': ''})


    Deserialize = DeserializeResponse(response)


    with open('response.json', 'w') as outfile:
        json.dump(response, outfile)
def main():
    try:
         if robotCheck:
             print "With Robot"
             broker = ALBroker("pythonBroker", "0.0.0.0", 0, IP_global, PORT)
             global pythonSpeechModule;
             pythonSpeechModule = SpeechRecoModule('pythonSpeechModule')
         else:
             print "Without Robot"
             TestConversation()
         StartIteration()
    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        sys.exit(0)
if __name__ == "__main__":
    main()

