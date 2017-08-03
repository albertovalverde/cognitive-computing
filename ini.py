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
import time
import cognitive_services
from naoqi import *
from PythonForNaomi import StartNaomi
from ftplib import FTP

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
        except Exception as e:
            self.asr = None
        self.memory = ALProxy("ALMemory")

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

        # Call to Cognitive services in Cloud
        self.CognitiveConnection.on_modified(filename)

        # Restart the iteration bucle
        StartIteration()


def StartIteration():
    if robotCheck:
        pythonSpeechModule.onLoad()
        pythonSpeechModule.onInput_onStart()
        time.sleep(200)
        pythonSpeechModule.onUnload()
    else:
        print "Without Robot"
        CognitiveConnection = cognitive_services.CognitiveService(IP_global, PORT, robotCheck)
        CognitiveConnection.on_modified("out.wav")

def confirmReadyForStartUp():
    print "\nReady to get started!"

def main():
    try:
         if robotCheck:
             print "With Robot"
             broker = ALBroker("pythonBroker", "0.0.0.0", 0, IP_global, PORT)
             global pythonSpeechModule;
             pythonSpeechModule = SpeechRecoModule('pythonSpeechModule')
         else:
             print "Without Robot"
             CognitiveConnection = cognitive_services.CognitiveService(IP_global, PORT, robotCheck)
             CognitiveConnection.on_modified("out.wav")

         StartIteration()

    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        sys.exit(0)

if __name__ == "__main__":
    main()
