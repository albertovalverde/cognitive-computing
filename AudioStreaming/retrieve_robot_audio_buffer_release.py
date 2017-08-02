# -*- coding: utf-8 -*-
###########################################################
# Retrieve robot audio buffer
# Syntaxe:
#    python scriptname --pip <ip> --help
#
#    --pip <ip>: specify the ip of your robot (without specification it will use localhost)
#    --help: print extra help
#
# Author: Alexandre Mazel
# Copyright: Aldebaran Robotics (c) 2014 - Please modify this script to fulfill your needs...
###########################################################

NAO_IP = "localhost"
# ~ NAO_IP = "10.0.164.132"
NAO_IP = "192.168.1.36"

from optparse import OptionParser
import naoqi
import numpy as np
import time
import sys


class SoundReceiverModule(naoqi.ALModule):
    """
    Use this object to get call back from the ALMemory of the naoqi world.
    Your callback needs to be a method with two parameter (variable name, value).
    """

    def __init__(self, strModuleName, strNaoIp):
        try:
            naoqi.ALModule.__init__(self, strModuleName);
            self.BIND_PYTHON(self.getName(), "callback");
            self.strNaoIp = strNaoIp;
            self.outfile = None;
            self.aOutFileDesc = [None] * (16);  # ASSUME max nbr channels = 16
            self.aOutFilename = []

        except BaseException, err:
            print("ERR: SoundReceiverModule: loading error: %s" % str(err));

    # __init__ - end
    def __del__(self):
        print("INF: SoundReceiverModule.__del__: cleaning everything");
        self.stop();

    def start(self, nSampleRate=48000, nChannelConfiguration=0, bSaveOneFilePerChannel=False, bExportAsWav=True,
              bVerbose=False):
        """
        - nChannelConfiguration: ALL_Channels: 0,  AL::LEFTCHANNEL: 1, AL::RIGHTCHANNEL: 2; AL::FRONTCHANNEL: 3  or AL::REARCHANNEL: 4.
            On Romeo, here's the current order: 1: right, 2: rear, 3: left, 4: front.
            On Pepper, here's the current order: ?

        - bSaveOneFilePerChannel: False => one wav with interleaved datas, else one file per channels
        - bExportAsWav: see --help
        """

        self.bExportAsWav = bExportAsWav
        self.bVerbose = bVerbose
        if self.bExportAsWav:
            from abcdk import sound
            # import abcdk.sound # from Aldebaran Behavior Complementary Development Kit

        ad = naoqi.ALProxy("ALAudioDevice", self.strNaoIp, 9559);
        nChannelConfiguration = nChannelConfiguration;  # ALL_Channels: 0,  AL::LEFTCHANNEL: 1, AL::RIGHTCHANNEL: 2; AL::FRONTCHANNEL: 3  or AL::REARCHANNEL: 4.
        nDeinterleave = 0;
        self.nSampleRate = nSampleRate;
        print("INF: SoundReceiver: samplerate: %dHz" % self.nSampleRate);
        ad.setClientPreferences(self.getName(), self.nSampleRate, nChannelConfiguration,
                                nDeinterleave);  # setting same as default generate a bug !?!
        self.bSaveOneFilePerChannel = bSaveOneFilePerChannel
        ad.subscribe(self.getName());
        print("INF: SoundReceiver: started!");
        # self.processRemote( 4, 128, [18,0], "A"*128*4*2 ); # for local test

    def stop(self):
        print("INF: SoundReceiver: stopping...");
        audio = naoqi.ALProxy("ALAudioDevice", self.strNaoIp, 9559);

        for i in range(len(self.aOutFileDesc)):
            fd = self.aOutFileDesc[i]
            if fd != None:
                print("INF: closing file '%s'" % self.aOutFilename[i])
                fd.close();
                if self.bExportAsWav:
                    import abcdk.sound
                    abcdk.sound.repair(self.aOutFilename[i], bQuiet=True);

        audio.unsubscribe(self.getName());
        print("INF: SoundReceiver: stopped!");

    def processRemote(self, nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, buffer):

        print "entro en process"
        """
        This is THE method that receives all the sound buffers from the "ALAudioDevice" module
        """
        if self.bVerbose: print(
        "DBG: processRemote received: nbOfChannels: %d, nbrOfSamplesByChannel: %d, aTimeStamp: %s, len(buffer):%d" % (
        nbOfChannels, nbrOfSamplesByChannel, str(aTimeStamp), len(buffer)))

        aSoundDataInterlaced = np.fromstring(str(buffer), dtype=np.int16);
        aSoundData = np.reshape(aSoundDataInterlaced, (nbOfChannels, nbrOfSamplesByChannel), 'F');

        if 0:
            # compute average
            aAvgValue = np.mean(aSoundData, axis=1);
            print("avg: %s" % aAvgValue);

        if 0:
            # compute fft
            nBlockSize = nbrOfSamplesByChannel;
            signal = aSoundData[0] * np.hanning(nBlockSize);
            aFft = (np.fft.rfft(signal) / nBlockSize);
            print("fft: %s" % aFft)

        if 1:
            # compute peak
            aPeakValue = np.max(aSoundData);
            if (aPeakValue > 3000):
                print("Peak: %s" % aPeakValue);

        if 1:
            yourOwnProcess(self.nSampleRate, nbOfChannels, nbrOfSamplesByChannel, aTimeStamp,
                           buffer)  # add here your own processing doing whatever you want...

        bSaveToFile = 1
        if (bSaveToFile):
            # save to file
            if self.aOutFileDesc[0] == None:
                # open file(s)
                strFilenameOut = "out.raw";
                if (self.bExportAsWav):
                    strFilenameOut = strFilenameOut.replace(".raw", ".wav")
                if not self.bSaveOneFilePerChannel:
                    print("INF: Writing sound to '%s'" % strFilenameOut);
                    self.aOutFileDesc[0] = open(strFilenameOut, "wb");
                    self.aOutFilename.append(strFilenameOut)
                else:
                    # multi file
                    for nNumChannel in range(0, nbOfChannels):
                        if (self.bExportAsWav):
                            strFilenameOutChan = strFilenameOut.replace(".wav", "_%d.wav")
                        else:
                            strFilenameOutChan = strFilenameOut.replace(".raw", "_%d.raw")

                        strFilenameOutChan = strFilenameOutChan % (nNumChannel + 1)
                        self.aOutFileDesc[nNumChannel] = open(strFilenameOutChan, "wb")
                        self.aOutFilename.append(strFilenameOutChan)
                        print("INF: Writing other channel sound to '%s'" % strFilenameOutChan);

                if self.bExportAsWav:
                    import abcdk.sound
                    if not self.bSaveOneFilePerChannel:
                        wavTempJustForHeader = abcdk.sound.Wav();
                        wavTempJustForHeader.new(nSamplingRate=self.nSampleRate, nNbrChannel=nbOfChannels,
                                                 nNbrBitsPerSample=16);
                        wavTempJustForHeader.writeHeader(self.aOutFileDesc[0], bAddBeginOfDataChunk=True);
                    else:
                        for nNumChannel in range(0, nbOfChannels):
                            wavTempJustForHeader = abcdk.sound.Wav();
                            wavTempJustForHeader.new(nSamplingRate=self.nSampleRate, nNbrChannel=1,
                                                     nNbrBitsPerSample=16);
                            wavTempJustForHeader.writeHeader(self.aOutFileDesc[nNumChannel], bAddBeginOfDataChunk=True);

            if not self.bSaveOneFilePerChannel:
                aSoundDataInterlaced.tofile(self.aOutFileDesc[0]);  # wrote the n channels in one file
            else:
                for nNumChannel in range(0, nbOfChannels):
                    aSoundData[nNumChannel].tofile(self.aOutFileDesc[nNumChannel]);


                    # processRemote - end

    def version(self):
        return "0.6";
        # SoundReceiver - end


def yourOwnProcess(nSampleRate, nbOfChannels, nbrOfSamplesByChannel, aTimeStamp, buffer):
    """
    implement here whatever you want
    """

    pass


# yourOwnProcess - end




def main():
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
    print "hice start"
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        SoundReceiver = None
        myBroker.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()