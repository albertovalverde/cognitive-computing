def getIP():
    text_fileIP = open("../Resources/IP.txt", "r")
    currentipdocument = text_fileIP.readlines()
    IP_ = currentipdocument[0]
    text_fileIP.close()
    print "Type in Naomi's IP address.\nIf this is Naomi's IP address, just hit enter.\n", IP_
    IPDefining = raw_input()
    if IPDefining == '':
        return IP_
    else:
        text_fileIP = open("../Resources/IP.txt", "w")
        IP_ = IPDefining
        text_fileIP.write(IP_)
        text_fileIP.close()
        return NAO_IP

PORT = 9559
NAO_IP = getIP() # Get Essi's IP address



import sys
import time
from optparse import OptionParser

import naoqi

import retrieve_robot_audio_buffer_release


def main():
    """ Main entry point



    """

    print "ESTO ES MAIN"

    SoundReceiverModule= retrieve_robot_audio_buffer_release.SoundReceiverModule

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
        pip=NAO_IP,
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
    myBroker = naoqi.ALBroker("myBroker",
                              "0.0.0.0",  # listen to anyone
                              0,  # find a free port and use it
                              pip,  # parent broker IP
                              pport)  # parent broker port

    # Warning: SoundReceiver must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global SoundReceiver
    SoundReceiver = SoundReceiverModule("SoundReceiver", pip)
    SoundReceiver.start(nSampleRate=nSampleRate, nChannelConfiguration=nChannelConfiguration,
                        bSaveOneFilePerChannel=bSaveOneFilePerChannel, bExportAsWav=bExportAsWav, bVerbose=bVerbose)



    time.sleep(5) # for testing
    print "Interrupted by user, shutting down"
    SoundReceiver = None
    #myBroker.shutdown()
    import PlayAudio
    PlayAudio.play("hello.wav") #change for "out.wav" for retrieve_robot_audio_buffer_release.py
    sys.exit(0)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        SoundReceiver = None
        myBroker.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()