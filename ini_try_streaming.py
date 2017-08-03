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
from optparse import OptionParser
from AudioStreaming import retrieve_robot_audio_buffer_release

# ~--- Initial startup stuff ---~#
robotCheck = StartNaomi.checkIfRobotIsConnected()  # Check if robot is connected
PORT = 9559  # Get Naomi's port
IP_global = StartNaomi.getIP(robotCheck)  # Get Naomi's IP address



def StartStreaming():
    """ Main entry point



    """

    print "ESTO ES MAIN"

    parser = OptionParser()
    parser.add_option("--pip",
                      help="Parent broker port. The IP address or your robot",
                      dest="pip")
    parser.add_option("--pport",
                      help="Parent broker port. The port NAOqi is listening to",
                      dest="pport",
                      type="int")
    parser.add_option("-s", "--samplerate",
                      help="Samplerate (default:48000)",
                      dest="nSampleRate",
                      type="int")
    parser.add_option("-c", "--channel_configuration",
                      help="0: 4 channels; 1: left, 2: right, 3: front, 4: rear.",
                      dest="nChannelConfiguration",
                      type="int")
    parser.add_option("-m", "--multifiles",
                      help="it will generated one different sound file for each channel",
                      dest="bSaveOneFilePerChannel",
                      action="store_true")

    parser.add_option("-w", "--wav_format",
                      help="enables this to use wav format instead of raw (requires an abcd kit installed)",
                      dest="bExportAsWav",
                      action="store_true")

    parser.add_option("-r", "--raw_format",
                      help="enables this to use raw format instead of wav",
                      dest="bExportAsWav",
                      action="store_false")

    parser.add_option("-v", "--verbose",
                      help="enables this to see extra log",
                      dest="bVerbose",
                      action="store_true")

    parser.add_option("-q", "--quiet",
                      help="enables this to remove extra log",
                      dest="bVerbose",
                      action="store_false")

    parser.set_defaults(
        pip=IP_global,
        nSampleRate=48000,
        nChannelConfiguration=0,
        bSaveOneFilePerChannel=False,
        bExportAsWav=True,
        bVerbose=False,
        pport=9559)

    (opts, args_) = parser.parse_args()
    pip = opts.pip
    pport = opts.pport
    nSampleRate = opts.nSampleRate
    nChannelConfiguration = opts.nChannelConfiguration
    bSaveOneFilePerChannel = opts.bSaveOneFilePerChannel
    bExportAsWav = opts.bExportAsWav
    bVerbose = opts.bVerbose

    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    # myBroker = naoqi.ALBroker("myBroker",
    #                           "0.0.0.0",  # listen to anyone
    #                           0,  # find a free port and use it
    #                           pip,  # parent broker IP
    #                           pport)  # parent broker port

    # Warning: SoundReceiver must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global SoundReceiver
    SoundReceiver = retrieve_robot_audio_buffer_release.SoundReceiverModule("SoundReceiver", pip)
    SoundReceiver.start(nSampleRate=nSampleRate, nChannelConfiguration=nChannelConfiguration,
                        bSaveOneFilePerChannel=bSaveOneFilePerChannel, bExportAsWav=bExportAsWav, bVerbose=bVerbose)
    print "hice start"
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print
    #     print "Interrupted by user, shutting down"
    #     SoundReceiver = None
    #     #myBroker.shutdown()
    #     sys.exit(0)

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

                StartStreaming()

                # self.tts = ALProxy("ALTextToSpeech", IP_global, PORT)
                # self.audio = ALProxy("ALAudioDevice", IP_global, PORT)
                # self.record = ALProxy("ALAudioRecorder", IP_global, PORT)
                # self.aup = ALProxy("ALAudioPlayer", IP_global, PORT)
                # # # # ----------> recording <----------
                # #print 'start recording...'
                # self.record_path = '/home/nao/out.wav'
                # self.record.stopMicrophonesRecording()
                # self.record.startMicrophonesRecording(self.record_path, 'wav', 16000, (0, 0, 1, 0))



                # ----------> playing the recorded file <----------
                #fileID = aup.playFile(record_path, 0.7, 0)



        except RuntimeError, e:
            self.mutex.release()
            self.onUnload()
            raise e
        self.mutex.release()

    def onWordRecognized(self, key, value, message):

        self.onUnload()

        try:

            SoundReceiver.stop()
        except:
            print "ERROR PERO SIGO"

        # self.record.stopMicrophonesRecording()
        # print 'record over'
        #
        filename = 'out.wav'
        # file = open(filename, 'wb')
        # self.ftp.retrbinary('RETR %s' % filename, file.write)

        # Call to Cognitive services in Cloud
        self.CognitiveConnection.on_modified("hello.wav")


        # try:
        #      SoundReceiver.exit()
        # except Exception:
        #     print Exception
        # Restart the iteration bucle
        StartIteration()


def StartIteration():
    if robotCheck:
        SoundReceiver=None
        pythonSpeechModule.onLoad()
        pythonSpeechModule.onInput_onStart()
        time.sleep(30)
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
