# -*- coding: utf-8 -*-
###########################################################
# Read a sound file, and send them to a socket
# syntaxe:
#       python scriptname ip port soundfilename 
#       eg: python scriptname localhost 50007 test12.wav
# Sound tools
# Aldebaran Robotics (c) 2008 All Rights Reserved
###########################################################

import socket
import struct

import abcdk.sound

def sendSounFileToServer( strHost, nPort, strFilename, nChannelNum = -1, bRemoveWavHeader = True, bPrefixDataWithSize = False ):
    """
    send this file to a open socket server
    - nChannelNum: audio channel to send (0..nbrchannel-1), -1 => all
    return 1 if ok or 0 on error
    """
    print( "INF: Opening '%s'" % strFilename )
    wav = abcdk.sound.Wav( strFilename )
    print( str(wav) )
    print( "INF: Wav duration: %5.2fs" % wav.rDuration )
    if( wav.rDuration < 0.001 ):
        print( "ERR: sounds seems empty (or not found), exiting..." )
        return 0
        
    if( nChannelNum != -1 ):
        print( "INF: sending channel %d/%d" % (nChannelNum, wav.nNbrChannel) )
        data = wav.data[nChannelNum::wav.nNbrChannel]
    else:
        data = wav.data
    nSizeDataInBytes = len(data)*wav.nNbrBitsPerSample/8
    print( "INF: sending %d samples (%d bytes) to %s:%s" % ( len(data), nSizeDataInBytes, strHost, nPort ) )
    for i in range(16):
        print( "data[%d]: 0x%04x" % (i,data[i]) )
    
    data = data.tostring()
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((strHost, nPort))
    
    if( bPrefixDataWithSize ):
        data = struct.pack('>I', nSizeDataInBytes) + data
    s.sendall( data ) # prefix with a 4 bytes network ordered containing the size
    print( "INF: everything has been sent..." )
    bFinishWithSomeBufferWithZeroes = False
    if( bFinishWithSomeBufferWithZeroes ):
        chZero = struct.pack('>I', 0 )
        sZero = chZero*1024*1024
        s.sendall( sZero )
        print( "INF: Zeroes has been sent also..." )
    s.close()
    
    print( "GOOD: Finished with success" )
    
    return 1
# sendFile - end
    
if( __name__ == "__main__" ):
    sendSounFileToServer( "localhost", 50007, "/home/likewise-open/ALDEBARAN/amazel/Bureau/sound_recording_sound/ears_test_recording/test4.wav", 0 )
    
    