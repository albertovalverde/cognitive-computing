# -*- coding: utf-8 -*-
#
# Quick view an image from depth camera of Nao
# v0.8
#
# Author: A.Mazel


#strNaoIp = "10.0.252.219"; # Benoit
#strNaoIp = "10.0.253.75"; # NaoAlex
#~ strNaoIp = "10.0.252.242";
strNaoIp = "10.0.160.237"; # NaoAlexV5
#~ strNaoIp = "10.0.204.126"; # PepperAlex
#~ strNaoIp = "198.18.0.1"; # Default Romeo



# using willowgarage official opencv 2.1 version
import cv2
import cv2.cv as cv

import os
import struct
import sys
import time

import random

# "small import from abcdk"  


def isOnNao():
    """Are we on THE real Nao ? - no abcdk version"""
    szCpuInfo = "/proc/cpuinfo";
    if not os.path.exists( szCpuInfo ): # already done by the getFileContents
        return False;
    szAllFile =  getFileContents( szCpuInfo, bQuiet = True );
    if( szAllFile.find( "Geode" ) == -1 and szAllFile.find( "Intel(R) Atom(TM)" ) == -1 ):
        return False;
    return True;
# isOnNao - end

def getNaoqiPath():
    "get the naoqi path"
    "we cut/paste this method here to not having to import the full module (cycle)"
    s = os.environ.get( 'AL_DIR' );
    if( s == None ):
        if( isOnNao() ):
            s = '/opt/naoqi/';
        else:
            s = '';
    return s;
# getNaoqiPath - end
def dumpHexa( anArray ):
    "dump a variable, even if containing binary"
    strTxt = "dumpHexa data len: %d\n" % len( anArray );
    i = 0;
    strAsciiLine = "";
    strTxt += "%03d: " % i;
    while( i < len( anArray ) ):
        strTxt += "%02x " % ord( anArray[i] );
        if( ord( anArray[i] ) > 20 ):
            strAsciiLine += "%s" % anArray[i];
        else:
            strAsciiLine += "_";
        i += 1;
        if( i % 8 == 0 ):
            strTxt += "  ";
        if( i % 16 == 0 ):
            strTxt += "  " + strAsciiLine + "\n";
            strTxt += "%03d: " % i;
            strAsciiLine = "";
    # while - end
    strTxt += "_"*3*(15-(i%16)); # end of line
    return strTxt + "     " + strAsciiLine + "\n";
# dumpHexa - end
#print( dumpHexa( "\t3213 Alexandre Mazel, happy happy man!\nYo!" ) );


def getPseudoColor( nValue, nMin = 0, nMax = 255, nErrorValue = -1 ):
    """
    Convert a color value to a pseudo color [r,g,b] representing the color in the value. (r,g,b in [0,255])
    nMin:             The min value to have the full "cold" value. (out of range will be in grey)
    nMax:            The max value to have the full "hot" value.
    nErrorValue:    You can specify an error value, that would be draw in white.
    """
    r, g, b = [0,0,0];
    # Invalid Data -> set Color to White
    if( nValue == nErrorValue ):
        r = 0xff;
        g = 0xff;
        b = 0xff;
    # Invalid Range
    # -> Set Color to Grey (debug)
    elif( nValue < nMin or nValue > nMax ):
        r = 0x80;
        g = 0x80;
        b = 0x80;
    else:
        # each part as a specific color computation
        # 5 parts:
        """
        nSizePhase = ( nMax - nMin ) / 5;
        if( nValue < nSizePhase * 1 ):
            r = 0xff;
            g = (((nValue-nMin)-0*nSizePhase)*0xff)/nSizePhase;
            b = 0x0;
        elif( nValue < nSizePhase * 2 ):
            r = 0xff - (((nValue-nMin)-1*nSizePhase)*0xff)/nSizePhase;
            g = 0xff;
            b = 0;
        elif( nValue < nSizePhase * 3 ):
            r = 0;
            g = 0xff;
            b = (((nValue-nMin)-2*nSizePhase)*0xff)/nSizePhase;
        elif( nValue < nSizePhase * 4 ):
            r = 0;
            g = 0xff - (((nValue-nMin)-3*nSizePhase)*0xff)/nSizePhase;
            b = 0xff;
        else:
            r = 0xff;
            g = 0;
            b = 0xff - (((nValue-nMin)-4*nSizePhase)*0xff)/nSizePhase;
        """
        # 2 parts: (green to yellow then yellow to red)
        nSizePhase = ( nMax - nMin ) / 2;
        if( nValue < nSizePhase * 1 ):
            r = (((nValue-nMin)-0*nSizePhase)*0xff)/nSizePhase;
            g = 0xff;
            b = 0x0;
        elif( nValue < nSizePhase * 2 ):
            r = 0xff;
            g = 0xff - (((nValue-nMin)-1*nSizePhase)*0xff)/nSizePhase;
            b = 0;    
    # else - end
    return [r,g,b];
# getPseudoColor - end

def swapArray( a1, a2 ):
    """
    swap the contents of two arrays.
    Both array must have the same size
    """
    assert( len(a1) == len(a2) );
    for i in range( len( a1 ) ):
        tmp = a1[i];
        a1[i] = a2[i];
        a2[i] = tmp;
    # for - end
# swapArray - end

def distSquared( x1, y1, x2, y2 ):
    return (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1);
    
def pointToWorld( nImageX, nImageY, rDepth, rMaxX = 320, rMaxY = 240, rFieldOfViewX = 60, rFieldOfViewY = 40 ):
    """
    convert a point from the depth array to a 3D world position (because the point if from an image in the cone)
    nImageX: [0..319]
    nImageY: [0..239]
    rFieldOfViewX: total field of view in degrees (so its half that aperture on each side)
    rDepthm: in meters
    return [rWorldX, rWorldY, rWorldZ<==>rDepth] all in meters
    """
    # convert to [-0.5,0.5]
    rCenteredX = ( nImageX / rMaxX ) - 0.5;
    rCenteredY = ( nImageY / rMaxY ) - 0.5;
    
    
# pointToWorld - end

def extractPeak( image, nSizeX, nSizeY, nMaxSize, nMaxNbr = 5, nErrorValue = -1 ):
    """
    Extract peak in an image, it's like a blob but without checking continuity
    Return: an array of peak [x,y,peak max value, avg size]
    nSize: size of the buffer
    nMaxSize: maximal size of one peak (a bigger peak will create two peaks)
    nMaxNbr: limit the number of returned peak
    """
    blobs = []; # will contain the center of the blob and it's max value
    nSmallerMax = 0; # the max value of the smallest  peak
    nSmallerIdx = -1;
    nMaxSizeSquared = nMaxSize*nMaxSize;
    for y in range( nSizeY ):
        for x in range( nSizeX ):
#            print( "x,y: %d,%d" % (x,y) );
            nVal = image[x+y*nSizeX];
            if( nVal != nErrorValue ):
                if( nVal > nSmallerMax ):
                    # update blobs
                    # find in blobs
                    bFound = False;                    
                    bUpdateSmallerMax = False;
                    n = 0;
                    while( n < len( blobs ) ):
                        if( distSquared( blobs[n][0], blobs[n][1], x, y ) < nMaxSizeSquared ):
                            # found it!
                            if( nVal > blobs[n][2] ):
                                # update this blobs
                                blobs[n][0] = x;
                                blobs[n][1] = y;
                                blobs[n][2] = nVal;
                                if( nSmallerMax == nVal ):
                                    # update smaller max
                                    bUpdateSmallerMax = True;
                            bFound = True;
                            break;
                        n += 1;
                    if( not bFound ):
                        # create a new one
                        if( len( blobs ) < nMaxNbr ):
                            # create from scratch
                            blobs.append( [x,y,nVal] );
                            bUpdateSmallerMax = True;
                        else:
                            # reuse smaller
                            blobs[nSmallerIdx][0] = x;
                            blobs[nSmallerIdx][1] = y;
                            blobs[nSmallerIdx][2] = nVal;
                            bUpdateSmallerMax = True;
                        
                    if( bUpdateSmallerMax ):
                        nSmallerMax = 0xFFFFFFF;
                        for idx, blob in enumerate( blobs ):
                            if( blob[2] < nSmallerMax ):
                                nSmallerMax = blob[2];
                                nSmallerIdx = idx;
#                    print( "blobs: %s" % str( blobs ) );
                # if( nVal > nSmallerMax ) - end
            # if( nVal != nErrorValue ) - end
            
    # convert to fixed size
    for idx, blob in enumerate( blobs ):
        blobs[idx].append( 50-idx*10 );

    return blobs;    
# extractPeak - end

# "small import from abcdk --- end"

def sample( depthMap, x, y, nSizeX, nSampleHalfSize = 2 ):
    rSum = 0;
    nElem = 0;
    for j in range( -nSampleHalfSize, nSampleHalfSize, 1 ):
        for i in range( -nSampleHalfSize, nSampleHalfSize, 1 ):
            rSum += depthMap[(y+j)*nSizeX+(x+i)]
            nElem += 1;
    return rSum/nElem;        
# sample - end

def convertFromUncalibrated( depthMap ):
    # 0.5m => 0.655
    # 3m => 2.12
    # 4m => 2.57
    # 6.45m => 3.38 => extropolated: 9m => 4.223
    rLim1 = 500.; rVal1 = 655
    rLim2 = 3000.; rVal2 = 2120
    rLim3 = 4000.; rVal3 = 2570
    rLim4 = 9000.; rVal4 = 4223
    
    #~ depthMap = ndarray(depthMap);
    timeBegin = time.time();
    rCoef21 = (rLim2-rLim1)/(rVal2-rVal1);
    rCoef32 = (rLim3-rLim2)/(rVal3-rVal2);
    rCoef43 = (rLim4-rLim3)/(rVal4-rVal3);
    if( False ):
        for i in range( len( depthMap ) ):
            rVal = depthMap[i];
            #~ rVal = 1560
            assert( rVal <= rLim4 );        
            if( rVal < rVal1 ):
                rVal = rLim1;
            elif( rVal < rVal2 ):
                rVal = rLim1 + (rVal-rVal1)*rCoef21;
            elif( rVal < rVal3 ):
                rVal = rLim2 + (rVal-rVal2)*rCoef32;
            else:
                rVal = rLim3 + (rVal-rVal3)*rCoef43;
            depthMap[i] = rVal;
    else:
        depthMap[ (depthMap < rVal1) ] = rLim1;
        mask = (depthMap >= rVal1) & (depthMap < rVal2 )
        depthMap[ mask  ] = 0;
    rDuration = time.time() - timeBegin;
    print( "rDuration: %5.3fs" % rDuration );
# convertFromUncalibrated - end

# import naoqi lib
strPath = getNaoqiPath();
home = `os.environ.get("HOME")`

if strPath == "None":
  print "the environnement variable AL_DIR is not set, aborting..."
  sys.exit(1)
else:
  #alPath = strPath + "/extern/python/aldebaran"
  alPath = strPath + "\\lib\\"
  alPath = alPath.replace("~", home)
  alPath = alPath.replace("'", "")
  sys.path.append(alPath)
  import naoqi
  from naoqi import ALBroker
  from naoqi import ALModule
  from naoqi import ALProxy

# turn off all NAO's leds
led = ALProxy( "ALLeds",  strNaoIp, 9559 );
led.fade( "AllLeds", 0., 0. );

mem = ALProxy( "ALMemory",  strNaoIp, 9559 );

nSizeX = 320;
nSizeY = 240;
bufferImageToDraw = cv.CreateImage( (nSizeX, nSizeY), cv.IPL_DEPTH_8U, 3 );
depthMap = [0]*nSizeX*nSizeY;

strDebugWindowName = "Depth"; # "DebugWindow"; # set to false to have no debug windows
cv.NamedWindow( strDebugWindowName, cv.CV_WINDOW_NORMAL );
cv2.moveWindow( strDebugWindowName, 0, 0 );
cv2.resizeWindow( strDebugWindowName, 640, 480 );


avd = ALProxy( "ALVideoDevice",  strNaoIp, 9559 );
# avd.setResolution( 1 ); # doesn't exists!
nCameraID = 2; # kDepthCamera
nResolution = 1;
nColorSpace = 17; # AL::kDepthColorSpace
# nColorSpace = 19; # AL::kXYZColorSpace
nFps = 30;
print( "avd.hasDepthCamera(): %s" % avd.hasDepthCamera() );
strSubscriberName = "NAO_3D_Viewer";
strSubscriberName = avd.subscribeCamera( strSubscriberName, nCameraID, nResolution, nColorSpace, nFps );

mem = ALProxy( "ALMemory",  strNaoIp, 9559 );

bKeyPressed = False;
nCptFrame = 0;
timeBegin = time.time();
bSaveFrame = False;

nScaleMultiplier = 320/nSizeX; # the algorithm is made for 320, so when we are in 160, we need to multiply stuffs

if( True ):
    # Asus:
    nMinValue = 400;
    nMaxValue = 9000;
    
if( False ): 
    # Pmd:
    nMinValue = 50;
    nMaxValue = 3000;

nIntegrationTime = 1000; # default: 1000ms, max: 3000ms (but warm the camera) see farest
kCameraExposureID = 17;
rVal = avd.getParameter( nCameraID, kCameraExposureID );
rVal = avd.setParameter( nCameraID, kCameraExposureID, nIntegrationTime );
print( "kCameraExposureID, val: %s (0x%x)" % (str( rVal ), rVal ) );

kConfidenceExposure = 36;
nConfidenceExposure = 2000;
rVal = avd.getParameter( nCameraID, kConfidenceExposure,  );
rVal = avd.setParameter( nCameraID, kConfidenceExposure, nConfidenceExposure );
print( "kConfidenceExposure, val: %s" % str( rVal ) );

bExtractBlob = False;
rAvgCenter = 0;
bDetectObstacles = True;
while( not bKeyPressed ):
    #~ try:
    if( True ):
        dataImage = avd.getImageRemote(strSubscriberName); # Image is in 320*240, (sometimes)
        #~ print( len(dataImage ) );
        #~ for i in range( 11 ):
            #~ print( "%d: %s" % (i, str( dataImage[i] ) ) );
        
        # print( dumpHexa( dataImage ) );        
        
        if( dataImage == None ):
            print( "ERR: dataImage is none!" );
        else:
            nSizeX = dataImage[0];
            nSizeY = dataImage[1];
            nNbrLayer = dataImage[2];
            nColorSpace = dataImage[3];
            nTimeStamp1 = dataImage[4];
            nTimeStamp2 = dataImage[5];
            image = dataImage[6];
            nCameraID = dataImage[7];
            nLeftAngle, nTopAngle, nRightAngle, nBottomAngle = dataImage[8:];
            if( 0 ):
                import numpy
                print dataImage[0];
                print dataImage[1];
                print dataImage[2];
                image = numpy.frombuffer( dataImage[6], dtype='uint16' );
                print image[0::16];
            if( bDetectObstacles ):
                # obstacles detection
                # minimal distance on my pepper is 69cm to the camera, 54cm to the front of the base
                import numpy
                print dataImage[0];
                print dataImage[1];
                print dataImage[2];
                w = dataImage[0];
                h = dataImage[1];
                image = numpy.frombuffer( dataImage[6], dtype='uint16' );
                
            if( False ):
                # small debug
                print( "Image get: %dx%d" % (nSizeX,nSizeY) );
                print( "Image prop: layer: %d, format: %d" % (nNbrLayer, nColorSpace) );
                if( False ):
                    i = 0;
                    while( i < 16 ):
                        print( "image: %d: %s" % (i, struct.unpack_from( "H", image, i )[0] ) ); #struct.calcsize(fmt)
                        i += struct.calcsize( "H" );
            
            # bufferImageToDraw.data = image;
            if( False ):
                # converted locally in NAO's  head, impossible for this camera !
                cv.SetData( bufferImageToDraw, image );
            else:
                # manual conversion
                i = 0;
                x = 0;
                y = 0;
                while( y < nSizeY ):
                    #~ print( "x,y: %d,%d" % (x,y) );
                    nValue = struct.unpack_from( "H", image, i )[0]; # H is unsigned short
                    i += struct.calcsize( "H" );
                    if( True ):
                        r, g, b = getPseudoColor( nValue, nMinValue, nMaxValue, 0 );
                    else:
                        r = (nValue*255) / nMaxValue;
                        g = b = r;
                    
                    bufferImageToDraw[y,x] = ( b, g, r );
                    depthMap[x+y*nSizeX] = nValue; # to help the peak detection, you need to invert it: = nMaxValue-nValue
                    x += 1;
                    if( x >= nSizeX ):
                        x = 0;                        
                        y += 1;
                # while - end
                
            nCenter = depthMap[ (nSizeY/2)*nSizeX + nSizeX/2 + 0];
            nCenter += depthMap[ (nSizeY/2)*nSizeX + nSizeX/2 + 1];
            nCenter += depthMap[ (nSizeY/2)*nSizeX + nSizeX/2 + nSizeX];
            nCenter += depthMap[ (nSizeY/2)*nSizeX + nSizeX/2 + nSizeX + 1];
            nCenter = nCenter/4; # if inverted, reinvert it back: = nMaxValue - nCenter/4
            #~ rAvgCenter = rAvgCenter * 0.7 + nCenter * 0.3;
            print( "nCenter: %4d, rAvgCenter: %5.3f" % ( nCenter, rAvgCenter/1000. ) );
            # 0.655 0.5m
            # 0.9 => 1m # TL 0.82 BR 0.86
            # 1.2 => 1.5m
            # 1.56 => 2m
            # 1.84 => 2.5m
            # 2.12 => 3m
            # 2.33 => 3.5m
            # 2.57 => 4m
            # 2.75 => 4.5m
            # 3.38 => 6.45m
            if( 0 ):
                convertFromUncalibrated( depthMap );

                
            
            
            cv.ShowImage( strDebugWindowName, bufferImageToDraw ); # ici ca fait crashhhhhheeeeeerrrr !
            nCptFrame +=1;
            bSaveFrame = bSaveFrame or mem.getData( "Device/SubDeviceList/Head/Touch/Front/Sensor/Value" ) > 0.5;
            if( bSaveFrame ):
                strFilename = "camera_viewer_%5.2f.png" % time.time();
                print( "Saving image to %s" % strFilename );
                led.fade( "AllLeds", 1., 0.2 );
                cv.SaveImage( strFilename, bufferImageToDraw ); # save last image at quit
                led.fade( "AllLeds", 0., 0.1 );
                bSaveFrame = False;
            if( nCptFrame == 20 ):
                rDuration = time.time() - timeBegin;
                print( "fps: %f" % (20/rDuration) );
                nCptFrame = 0;
                timeBegin = time.time();
    #~ except BaseException, err:
        #~ print( "ERR: camera_viewer: (err:%s)" % (str(err)) );
        
    nKey =  cv.WaitKey(1);
    bKeyPressed = ( nKey == ord( 'q' ) );
    bSaveFrame = ( nKey == ord( 's' ) );
    bTestFrame = ( nKey == ord( 't' ) );
# while - end
#cv.SaveImage( "camera_viewer_at_exit.png", bufferImageToDraw ); # save last image at quit

print("Unsbscribing..." );
avd.unsubscribe(strSubscriberName);

print("The end..." );