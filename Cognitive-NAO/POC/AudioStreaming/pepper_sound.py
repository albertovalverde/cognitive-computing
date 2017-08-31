# -*- coding: utf-8 -*-
 
"""Pepper?????????PC?????????????????????"""
 
import argparse
import sys
import time
 
import qi
from pyaudio import PyAudio
 
class SoundDownloadPlayer(object):
    """
    Service for download and play sound which Pepper here in real-time.
    PyAudio is required.
    """
 
    def __init__( self, app):
        """Initialize service and PyAudio stream"""
 
        super(SoundDownloadPlayer, self).__init__()
        app.start()
        session = app.session
 
        self.robot_audio = session.service("ALAudioDevice")
 
    @qi.nobind
    def start(self, serviceName):
        """Start processing"""
 
        self.pyaudio = PyAudio()
        #?????????:
        #format "2": ????????16bit=2byte
        #channels "1": ???????
        #rate "16000": ?????????
        self.pyaudioStream = self.pyaudio.open(
            format=self.pyaudio.get_format_from_width(2),
            channels=1,
            rate=16000,
            output=True
            )
        #16000Hz, 3?????????0?????????????????
        self.robot_audio.setClientPreferences(serviceName, 16000, 3, 0)
        self.robot_audio.subscribe(serviceName)
        #Ctrl + C ??????
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
 
        self.robot_audio.unsubscribe(serviceName)
        self.pyaudioStream.close()
        self.pyaudio.terminate()
        print("SoundDownloadPlayer stopped successfully.")
 
    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        """Write to pyaudio stream buffer to play real-time"""
        #print("process remote called")
        self.pyaudioStream.write(str(inputBuffer))
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.1.34",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
 
    args = parser.parse_args()
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application(["MySoundDownloadPlayer", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
 
    player = SoundDownloadPlayer(app)
    app.session.registerService("MySoundDownloadPlayer", player)
    player.start("MySoundDownloadPlayer")
 #python pepper_sound.py --ip 192.168.xx.xx --port 9559