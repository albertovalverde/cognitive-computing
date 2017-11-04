#!/usr/bin/env python
import time

from audio import get_string
import nao_parser
import threading
import json, pickle, sys
from PythonForNaomi import RobotFunctions, StartNaomi
from watson_developer_cloud import ConversationV1

config = pickle.load(
    open('Config/configurationDictionary.pkl', 'rb'))  # Loads configuration .pkl file into a Python dictionary
credentials = json.load(open('Config/credentials.json'))  # Loads all Bluemix credentials
ID_conversation = credentials["region"][config["regionVr"]]["Conversation"]["ID"]
User_conversation =  credentials["region"][config["regionVr"]]["Conversation"]["username"]
Pass_conversation =  credentials["region"][config["regionVr"]]["Conversation"]["password"]

conversation = ConversationV1(
            username=User_conversation,
            password=Pass_conversation,
            version='2016-09-20')
        # # replace with your own workspace_id
workspace_id = ID_conversation

# ~--- Initial startup stuff ---~#
robotCheck = StartNaomi.checkIfRobotIsConnected()  # Check if robot is connected
PORT = 9559  # Get Naomi's port
IP_global = StartNaomi.getIP(robotCheck)  # Get Naomi's IP address

class Filteresponse:
    text = ""
    classified = ""
    playgame = ""
    playresponse=""
    playcolor=""
    intents = ""
    inputText = ""
    entities = ""


class SpeechRecoModule():
    def __init__(self):
        self.Naomi = RobotFunctions.Robot(IP_global, PORT, config,
                                          robotCheck)  # Initialise all robot functions in variable "Naomi"
        self.Naomi.StartUp()  # Get Naomi out of rest mode, stand it up, set eye colour, etc.
        self.response = conversation.message(workspace_id=workspace_id,
                                        message_input={'text': ''})

        print  str(self.response["output"]["text"][len(self.response["output"]["text"])-1])

    def speech_recognition_loop(self):
        while True:
            try:
                string = get_string()
            except LookupError as e:
                print e
            else:
                self.response = conversation.message(workspace_id=workspace_id,
                                                     message_input={'text': str(string)}, context=self.response['context'])

                Deserialize = DeserializeResponse(self.response)

                self.Naomi.printAndSay(Deserialize.text)


    def face_detection_loop(self):
        pass

def DeserializeResponse(response):
        print(json.dumps(response, indent=2))
        deserialize= Filteresponse
        try:
            deserialize.text = response["output"]["text"][len(response["output"]["text"])-1]
            print "text : " + deserialize.text
        except:
            deserialize.text = None
        try:
            deserialize.intents = response["intents"][0]["intent"]
            print "intents : " + deserialize.intents
        except:
            deserialize.intents = None
        try:
            deserialize.entities = response["entities"][0]["value"]
            print "entitie : " + deserialize.entities
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
            print "play_response : " + deserialize.playresponse
        except:
            deserialize.playresponse = None
        try:
            deserialize.playcolor = response["context"]["play_color"]
            print "play_color : " + deserialize.playcolor
        except:
            deserialize.playcolor = None
        try:
            deserialize.inputText = response["input"]["text"]
            print "input text : " + deserialize.inputText
        except:
            deserialize.inputText = None
        return deserialize


def main():
    try:

        pythonSpeechModule = SpeechRecoModule()
        sr_t = threading.Thread(None, pythonSpeechModule.speech_recognition_loop(), "sr_t")
        sr_t.start()
        fd_t = threading.Thread(None, pythonSpeechModule.face_detection_loop(), "fd_t")
        fd_t.start()

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        sys.exit(0)

if __name__ == "__main__":
    main()


