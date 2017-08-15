# -*- coding: utf-8 -*-

#
# Quick view an image from Nao
#
# v0.7
#
# You need to enter the IP of your NAO in the configuration section.
# Then you could change the wanted resolution, nbr camera or ...
#
# Author: A.Mazel

import copy
import math
import numpy

# some constants

kQQVGA = 0;
kQVGA = 1;
kVGA = 2;
k4VGA = 3; # work only on a NAO V4

kGrey = 0;
kYUV422 = 9;
kRGB = 11;
kBGR = 13;

kFlipH = 7;
kFlipV = 8;
kSelectCamera = 18;

kCameraAutoExpositionID = 11;
kCameraAutoWhiteBalanceID = 12;
kCameraExposureID = 17;
kCameraGainID = 6;


#
# Configuration
#

#strNaoIp = "10.0.252.219"; # Benoit
#strNaoIp = "10.0.253.75"; # NaoAlex
#~ strNaoIp = "10.0.253.68"; # NaoAlex16
#~ strNaoIp = "10.0.254.27"; # stereo2
#~ strNaoIp = "10.0.254.176"; # Manu3D
#strNaoIp = "10.0.254.54"; # Laurent3D
strNaoIp = "192.168.1.141"; # TheFreak
strNaoIp = "10.0.253.99"; # NaoAlexBlue
strNaoIp = "10.0.254.120"; # Romeo
strNaoIp = "bebedege.local"
strNaoIp = "198.18.0.1" # Default Romeo
#~ strNaoIp = "10.0.206.199" # NaoAlexV5
#~ strNaoIp = "10.0.204.18" # PepperAlex
#~ strNaoIp = "10.0.161.16" # PepperAlex
#~ strNaoIp = "NaoLaurentV5BT.local"
#~ strNaoIp = "10.0.164.226"
#~ strNaoIp = "192.168.100.210"
strNaoIp = "10.0.164.245"
strNaoIp = "10.0.165.65"
strNaoIp = "10.0.207.34"

nWantedResolution = kVGA;
bOutputTimeStampToFilename = False;
anVFlipCamera = [0, 0]; # normal settings
anHFlipCamera = [0, 0];
    
bUseMultiStreamModule = False;
#~ bUseMultiStreamModule    = True;

bStereoMode = False;
bStereoMode = True; # else it's top/bottom

bMoveEyes = False;

bBlinkWhenSaving = True;

bRomeoMode = True
if( bRomeoMode ):
    bStereoMode = True

if( bMoveEyes ):
    bUseMultiStreamModule = False;



nColorSpace = kBGR;
nColorSpace = kYUV422;
#~ nColorSpace = kGrey;

if( bUseMultiStreamModule ):
    if( nWantedResolution == k4VGA ):
        nWantedResolution = kVGA;

if( bUseMultiStreamModule and bStereoMode ):
    anVFlipCamera = [0, 1]; # stereo settings (was [0,1])
    anHFlipCamera = [0, 1];
    
if( bRomeoMode ):
    anVFlipCamera = [0, 0];
    anHFlipCamera = [0, 0];

kTopCamera = 0;
kBottomCamera = 1;
nCameraToUse = kTopCamera;
#~ nCameraToUse = kBottomCamera;

try:
    import cv # using willowgarage official opencv 2.1 version # http://opencv.willowgarage.com/documentation/python/ (windows: install full openpackage cv, then copy C:\opencv\build\python\2.6 to sites-package)
except:
    print( "WRN: nao_camera_viewer: NO OpenCV library ???" );
try:    
    import cv2 # using opencv 2.4.5 # http://opencv.org # on windows: copy cv2.pyd from ...\opencv\build\python\2.7 to c:\python27\
    import cv2.cv as cv # backward compatible
except:
    print( "WRN: nao_camera_viewer: NO OpenCV2 library ???" );
    
try:
    import numpy
except:
    print( "WRN: nao_camera_viewer: NO numpy found, you won't have yuv => bgr conversion!" );

#~ import cv.simpleblobdetector
#~ print( dir( cv ) );




import os
import sys
import time

"small import from abcdk"

def getFileContents( szFilename, bQuiet = False ):
    "read a file and return it's contents, or '' if not found, empty, ..."
    aBuf = "";
    try:
        file = open( szFilename );
    except BaseException, err:
        if( not bQuiet ):
            print( "ERR: filetools.getFileContents open failure: %s" % err );
        return "";
        
    try:
        aBuf = file.read();
    except BaseException, err:
        if( not bQuiet ):
            print( "ERR: filetools.getFileContents read failure: %s" % err );
        file.close();
        return "";
        
    try:
        file.close();
    except BaseException, err:
        if( not bQuiet ):
            print( "ERR: filetools.getFileContents close failure: %s" % err );
        pass
    return aBuf;
# getFileContents - end



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

# import from naoqi - end

def test( bufferImage, strTrainoutFile ):
    "return object found"
    "[obj1,obj2, ...]"
    "with obj: [[x,y,w,h],neighbors]"    
    image_size = cv.GetSize(bufferImage);
    # create grayscale version
    grayscale = cv.CreateImage( image_size, cv.IPL_DEPTH_8U, 1 );
    cv.CvtColor( bufferImage, grayscale, cv.CV_BGR2GRAY ); # this is crashing
    # create storage
    storage = cv.CreateMemStorage(0);
    # equalize histogram
    cv.EqualizeHist(grayscale, grayscale);
 
    # detect objects
    #cascade = cv.Load('D:\pythonscript\data\haarcascades\haarcascade_frontalface_alt.xml');
    cascade = cv.Load(strTrainoutFile);
    
    objects = cv.HaarDetectObjects(grayscale, cascade, storage, 1.2, 15, cv.CV_HAAR_DO_CANNY_PRUNING, (50, 50) );
 
    nNbr = 0;
    if objects:
        nNbr = len( objects );
        print( "INF: test: %d Object(s) detected! (data: %s)" % (nNbr, str(objects) ) );
        for obj in objects:
            print( "obj: %s" % str( obj ) );
            rect = obj[0];
            cv.Rectangle( bufferImage, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), cv.RGB(0, 255, 0), 3, 8, 0);
            
    else:
        print( "INF: test: NO OBJ DETECTED!" );
        
    return objects;
# test - end

def equalizeColorImage( imageBuffer, bEqualiseEachChannelIndependantly = False ):
    """
    Take a rgb image and expand it its contrast    
    - bEqualiseEachChannelIndependantly: 
        - False: expand it so that at least one channel have maximum value and one have minimum value (it could be the same). colors are preserved
        - True: expand it so that every channel has its maximum range, independantly (resulting color balance could be unnatural, biased, ...)
    Return True if the image has been equalized (or else it doesn't need or can't be)
    """
    nNbrChannel = 3;
    aMin = [255] * 3;
    aMax = [0] * 3;
    for i in range( nNbrChannel ):
        cv.SetImageCOI(  imageBuffer, i+1 ); # COI: 0: all, 1: first channel, ...
        retVal = cv.MinMaxLoc( imageBuffer );
        if( aMin[i] > retVal[0] ):
            aMin[i] = retVal[0];
        if( aMax[i] < retVal[1] ):
            aMax[i] = retVal[1];
            
    nMin = min( aMin );
    nMax = max( aMax );
    cv.SetImageCOI(  imageBuffer, 0 ); # remove COI
    
    #~ print( "INF:equalizeColorImage: min: %d, max: %d (channel: %s, %s)" % ( nMin, nMax, str(aMin), str(aMax) ) );
    
    if( not bEqualiseEachChannelIndependantly ):
        if( nMin <  10 and nMax > 230 ):
            # it's not so bad...
            return False;
    else:        
        aWorstMin = max( aMin );
        aWorstMax = min( aMax );
        if( aWorstMin < 10 and aWorstMax > 230 ):
            # even the worst channel's not so bad...
            return False;
    
    if( nMin == nMax  ):
        # it's far too bad...
        return False;
        
    if( not bEqualiseEachChannelIndependantly ):
        cv.AddS( imageBuffer, -nMin, imageBuffer );
        rScale = 255. / (nMax - nMin);
        #~ print( "rScale: %f" % rScale );
        # cv.Mul( imageBuffer, None, imageBuffer, scale = rScale ); # complaints
        # imageBuffer.point(lambda i: i * 1.5 ); # doesn't work
        #imageBuffer = imageBuffer * 5; # doesn't work
        neutralImage = cv.CreateImage( cv.GetSize(imageBuffer), 8, nNbrChannel );
        cv.Set( neutralImage, [1]*nNbrChannel );
        cv.Mul( imageBuffer, neutralImage, imageBuffer, scale = rScale );
    else:
        bufferR = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
        bufferG = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
        bufferB = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );            
        cv.Split( imageBuffer, bufferB, bufferG, bufferR, None );
        
        neutralImage = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
        cv.Set( neutralImage, [1]*nNbrChannel );
        
        cv.AddS( bufferB, -aMin[0], bufferB );
        rScale = 255. / (aMax[0] - aMin[0])
        #~ print( "rScale: %f" % rScale );
        cv.Mul( bufferB, neutralImage, bufferB, scale = rScale );
        
        cv.AddS( bufferG, -aMin[1], bufferG );
        rScale = 255. / (aMax[1] - aMin[1]);
        #~ print( "rScale: %f" % rScale );        
        cv.Mul( bufferG, neutralImage, bufferG, scale = rScale );
        
        cv.AddS( bufferR, -aMin[2], bufferR );
        rScale = 255. / (aMax[2] - aMin[2]);
        #~ print( "rScale: %f" % rScale );        
        cv.Mul( bufferR, neutralImage, bufferR, scale = rScale );
        
        cv.Merge( bufferB, bufferG, bufferR, None, imageBuffer );
    return True;
# equalizeColorImage - end

def setParameterLoudly( nNumParam, value ):
    """
    change each parameter, loudly, so that we're sure it has been set
    """
    print( "INF: setParameterLoudly( %d, %s )" % ( nNumParam, str( value ) ) );
    avd = ALProxy( "ALVideoDevice",  strNaoIp, 9559 );
    for i in range( 5 ):
        bRet = avd.setParameter( 1, nNumParam, value );
        print( "bRet: %s" % str(bRet) );
        if( bRet ):
            break;
        time.sleep( 1.0 );
# setParameterLoudly - end

def setCameraParamForRedAndBlue( bSetOrUnset = True ):
    """
    remove all automation, so that the led colors are allways the same on all light condition
    - bSetOrUnset: True: set params, False: restore automation
    """
    kCameraBrightnessID = 0;
    kCameraContrastID = 1;
    kCameraSaturationID = 2;
    kCameraGainID = 6;
    kCameraAutoExpositionID = 11;
    kCameraAutoWhiteBalanceID = 12;
    kCameraExposureID = 17;
    kCameraSharpnessID = 24;
    kCameraWhiteBalanceID = 33;
    
    kCameraSetDefaultsParamsID = 19;
    
    avd = ALProxy( "ALVideoDevice",  strNaoIp, 9559 );
    
    # first we reset camera totally
    setParameterLoudly( kCameraSetDefaultsParamsID, 1 );
    setParameterLoudly( kCameraAutoExpositionID, 1 );
    setParameterLoudly( kCameraAutoWhiteBalanceID, 1 );
    if( not bSetOrUnset ):
        return;
    
    
    
    setParameterLoudly( kCameraAutoExpositionID, 1 );
    setParameterLoudly( kCameraBrightnessID, 108 );    # must be set when auto expos is auto (?!?)

    # remove automation    
    setParameterLoudly( kCameraAutoExpositionID, 0 );
    setParameterLoudly( kCameraAutoWhiteBalanceID, 0 );
    time.sleep( 0.5 );
    # specific settings
    setParameterLoudly( kCameraBrightnessID, 108 );
    setParameterLoudly( kCameraContrastID, 62 );
    setParameterLoudly( kCameraSaturationID, 255 );
    setParameterLoudly( kCameraGainID, 32 );
    setParameterLoudly( kCameraExposureID, 432 );
    setParameterLoudly( kCameraSharpnessID, 0 ); # avg sharpness
    setParameterLoudly( kCameraWhiteBalanceID, -86 );

        
# setParamForRedAndBlue - end

def getHotPoint( imageBuffer, bAsBinary = False ):
    """
    compute the average of position of an image (it's the average of every pixel, leveled by its' value)
    - bAsBinary: use every non null pixel as a full pixel
    return the hot point position or [-1,-1] if no pixel
    """
    nSumX = 0;
    nSumY = 0;
    nSumWeightedX = 0;
    nSumWeightedY = 0;    
    nSumXX = 0;
    nSumYY = 0;    
    nWeightedSum = 0;
    nNbrPixelHit = 0;
    nNbrPixel = imageBuffer.width * imageBuffer.height;
    x = 0;
    y = 0;
    while( y < imageBuffer.height ):
        nVal = imageBuffer[y,x];
        if( nVal > 0 ):
            #~ print( "x: %d, y: %d, val: %d" % (x,y,nVal) );
            if( bAsBinary ):
                nVal = 1;
            nSumX += x;
            nSumY += y;
            nSumWeightedX += nVal*x;
            nSumWeightedY += nVal*y;            
            nSumXX += x*x;
            nSumYY += y*y;            
            nWeightedSum += nVal;
            nNbrPixelHit += 1;
            
        x += 1;
        if( x == imageBuffer.width ):
            x = 0;
            y += 1;
    if( nWeightedSum < 1 ):
        return [-1,-1];
    nMedX = nSumX/nNbrPixelHit;
    nMedY = nSumY/nNbrPixelHit;
    nMedXX = nSumXX/nNbrPixelHit;
    nMedYY = nSumYY/nNbrPixelHit;
    nVarianceX = nMedXX-(nMedX*nMedX);
    nVarianceY = nMedYY-(nMedY*nMedY);
    
    rThreshold = 1400;
    if( nVarianceX > rThreshold or nVarianceY > rThreshold ):
        print( "WRN: abcdk.image.getHotPoint: Too much variance: nVarianceX: %d, nVarianceY: %d" % ( nVarianceX, nVarianceY ) );        
        return [-1,-1];
    
    return [int(nSumWeightedX/nWeightedSum), int(nSumWeightedY/nWeightedSum)];
# getHotPoint - end


def findRedAndBlueMarks( imageBuffer, imageBufferForDrawingDebug = None, _nDetectionMethod = 0 ):
    """
    find an intended red and blue mark. (needs to be as it must be).
    - imageBuffer: image to analyse
    - imageBufferForDrawingDebug: image to draw intermediate image computation
    - _nDetectionMethod: internal, in case of not found, we could test others method
    return [[xRed, yRed],[xBlue, yBlue]] or [[-1,y], [-1, y]] if not found
    """
    
    kDetectionMethodNbr = 2;
    
    equalizeColorImage( imageBuffer, bEqualiseEachChannelIndependantly = False );
    
    #~ cv.Threshold( imageBuffer, imageBuffer, 127, 18, cv.CV_THRESH_BINARY );
    #~ cv.SetImageCOI(  imageBuffer, 1 ); # a retester: c'est peut etre plus optimal (non: plein de méthode ne marche pas avec les COI)
    #~ grey = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
    workR = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
    workB = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
    
    if( True ):
        # removing other channels
        bufferR = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
        bufferG = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
        bufferB = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );            
        cv.Split( imageBuffer, bufferB, bufferG, bufferR, None ); # a tester et voir aussi pour le COI ?!?
        # possible value for threshold: CV_THRESH_BINARY, CV_THRESH_TOZERO, CV_THRESH_TOZERO_INV, ...
        nLimit = 64;
        if( True ):
            # set bad pixel to zero
            nType = cv.CV_THRESH_TOZERO;
            nReplace = 0;                    
        else:
            # set good pixel to full
            nType = cv.CV_THRESH_BINARY;
            nReplace = 255;                    
        cv.Threshold( bufferR, bufferR, nLimit, nReplace, nType );
        cv.Threshold( bufferG, bufferG, nLimit, nReplace, nType );
        cv.Threshold( bufferB, bufferB, nLimit, nReplace,  nType );
        cv.Sub( bufferR, bufferG, workR );
        cv.Sub( workR, bufferB,workR );
        cv.Sub( bufferB, bufferG, workB );
        cv.Sub( workB, bufferR,workB );
    else:
        # selecting pixels by color
        cv.InRangeS( imageBuffer, (0,0,64), (60,60,255), workR );
        cv.InRangeS( imageBuffer, (64,0,0), (255,60,60), workB );
        
    # find blobs
    #~ blopParams = cv.SimpleBlobDetector.params();

    if( _nDetectionMethod == 0 ):
        cv.Erode( workR, workR, iterations = 1 ); # with 1 it's better when surrounded by yellow
        cv.Erode( workB, workB, iterations = 1 ); # was 2, but faster with one, so...
    else:
        # erode more specialized
        morphShape = cv.CreateStructuringElementEx( 1, 3, 0, 1, shape=cv.CV_SHAPE_RECT );
        cv.Erode( workR, workR, element = morphShape, iterations = 1 );
        morphShape = cv.CreateStructuringElementEx( 1, 13, 0, 6, shape=cv.CV_SHAPE_RECT );
        cv.Erode( workB, workB, element = morphShape, iterations = 1 );
        #~ cv.Erode( workB, workB, iterations = 1 ); # was 2, but faster with one, so...
    
    cv.Threshold( workR, workR, 92, 255, cv.CV_THRESH_BINARY ); # remove weak red like orange or yellow ...
    cv.Threshold( workB, workB, 40, 0, cv.CV_THRESH_TOZERO ); # remove weak point
    
    #~ retVal = cv.MinMaxLoc( workR );
    #~ print( "retVal: %s" % str( retVal ) );
    #~ retVal = cv.Norm( workR, None, cv.CV_L2 );
    #~ print( "retVal: %s" % str( retVal ) );    
    #~ retVal = cv.Moments( bufferG, binary=True );
    #~ print( "retVal: %s" % str( retVal ) );
    #~ retVal = cv.MinMaxLoc( workR );            
    #~ x = retVal[3][0];
    #~ y = retVal[3][1];
    x1, y1 = getHotPoint( workR );
    
    #~ retVal = cv.MinMaxLoc( workB );
    #~ x = retVal[3][0];
    #~ y = retVal[3][1];
    x2, y2 = getHotPoint( workB );
    
    if( x1 == -1 or x2 == -1 ):
        if( _nDetectionMethod + 1 < kDetectionMethodNbr ):
            return findRedAndBlueMarks( imageBuffer, imageBufferForDrawingDebug, _nDetectionMethod = _nDetectionMethod+1 );
    
    if( False ):
        # to debug: write results in the image, to see selected pixels
        zeroChannel = cv.CreateImage( cv.GetSize(imageBuffer), 8, 1 );
        cv.Set( zeroChannel, [0]*1 );
        #~ cv.Threshold( workB, workB, 90, 255, cv.CV_THRESH_BINARY ); # highlight selected areas
        cv.Threshold( workB, workB, 40, 255, cv.CV_THRESH_BINARY ); # highlight all areas
        cv.Merge( workB, zeroChannel, workR, None, imageBuffer );    
    
    cv.Circle( imageBuffer, (x1, y1), 10, (0,0,255) );    
    cv.Circle( imageBuffer, (x2, y2), 10, (255,0,0) );
    
    if( y1 < y2 ):
        # red is above blue: error!
        x1 = x2 = -1;
    else:        
        if( abs( x2 - x1 ) > abs( y2-y1 ) ):
            # the point are not enough vertical
            x1 = x2 = -1;
    
    if( imageBufferForDrawingDebug != None ):
        imageBufferForDrawingDebug = workR;
    
    return [ [x1,y1], [x2,y2] ];
# findRedAndBlueMark - end

def limitRange( rVal, rMin, rMax ):
    "ensure that a value is in the range rMin, rMax"
    "WARNING: if rMin is less than rMax, there could be some strange behaviour"
    if( rVal < rMin ):
        rVal = rMin;
    elif( rVal > rMax ):
        rVal = rMax;
    return rVal;
# limitRange - end

def yuvToRgb( yuv ):
    "take an yuv array [y,u,v] (0..255) and return it in [r,g,b] (0..255)"
    "Attended value:"
    "red: [255,0,0] => [0°=>0,255,255]"
    y, u, v = yuv;
    r = limitRange( int( 1.164*(y - 16) + 1.596*(v-128) ), 0, 255 );
    g = limitRange( int( 1.164*(y - 16) - 0.813*(u-128) - 0.391*(v-128) ), 0, 255 );
    b = limitRange( int(1.164*(y - 16) + 2.018*(u-128) ), 0, 255 );
    return [ r, g, b];
# yuvToRgb - end

def convertYUV_ToBGR( bufferImageToDraw, image, nSizeX, nSizeY ):
    """
    WARNING: it's so slow, because it's at pixel level in python. Beurk
    """
    nIdxBuf = 0;
    for y in range(0, nSizeY):
        for x in range(0, nSizeX,2):
            #~ nVal = aBuf[x+y*nImageWidth];
            #~ y = ( nVal & 0xF0 ) >> 4;
            #~ u = ( nVal & 0x03 );
            #~ v = ( nVal & 0x0C ) >> 2;
            #~ print( "x: %s, y: %s, nIdxBuf: %s" % (x,y,nIdxBuf) );
            y1  = ord(image[nIdxBuf]);
            nIdxBuf += 1;
            u = ord(image[nIdxBuf]);
            nIdxBuf += 1;
            y2  = ord(image[nIdxBuf]);
            nIdxBuf += 1;
            v = ord(image[nIdxBuf]);
            nIdxBuf += 1;
            r,g,b = yuvToRgb( [y1,u,v] );
            bufferImageToDraw[y,x] = ( b, g, r );
            r,g,b = yuvToRgb( [y2,u,v] );
            bufferImageToDraw[y,x+1] = ( b, g, r );
# convertYUV_ToBGR - end

def convertRGB_ToBGR( bufferImageToDraw, image, nSizeX, nSizeY ):
    """
    WARNING: it's so slow, because it's at pixel level in python. Beurk
    """
    y = 0;
    while( y < nSizeY ):
        x = 0;
        while( x < nSizeX ):
            r = ord( image[(x+y*nSizeX)*3+0] );
            g = ord( image[(x+y*nSizeX)*3+1] );
            b = ord( image[(x+y*nSizeX)*3+2] );
            bufferImageToDraw[y,x] = ( r, g, b );
            x +=1;
        y += 1;
    # while - end
# convertRGB_ToBGR - end

def convertYUV_ToBGR_cv2( image, nSizeX, nSizeY ):
    """
    using the cv2 convert method
    """
    #~ timeBegin = time.time();
    numpyBuf = (numpy.reshape(numpy.frombuffer(image, dtype='%iuint8' % 1), ( nSizeX, nSizeY, 2)))
    rgb = cv2.cvtColor(numpyBuf, cv2.COLOR_YUV2BGR_YUYV); # COLOR_YUV2RGB_Y422 # cv2.COLOR_YUV2RGB_YUYV
    imageRgb = rgb.tostring();
    #~ rDuration = time.time() - timeBegin;
    #~ print( "rDuration: %s" % rDuration ); # ~1ms per conversion!
    return imageRgb;
# convertYUV_ToBGR_cv2 - end



# import naoqi lib
strPath = getNaoqiPath();
home = `os.environ.get("HOME")`

if strPath == "None":
  print "the environnement variable AL_DIR is not set, aborting..."
  sys.exit(1)
else:
  #alPath = strPath + "/extern/python/aldebaran"
  alPath = strPath + os.sep + "lib" + os.sep
  alPath = alPath.replace("~", home)
  alPath = alPath.replace("'", "")
  print( "Using naoqi from '%s'" % alPath );
  sys.path.append(alPath)
  import naoqi
  from naoqi import ALBroker
  from naoqi import ALModule
  from naoqi import ALProxy


# turn off all NAO's leds
try:
    led = ALProxy( "ALLeds",  strNaoIp, 9559 );
    led.fade( "AllLeds", 0., 0. );
except BaseException, err:
    print( "WRN: while setting leds to 0, err: %s" % str(err) );

mem = ALProxy( "ALMemory",  strNaoIp, 9559 );


strDebugWindowName = "Video Monitor"; # "DebugWindow"; # set to false to have no debug windows
cv.NamedWindow( strDebugWindowName, cv.CV_WINDOW_AUTOSIZE);
cv.MoveWindow( strDebugWindowName, 0, -1 );

if( bUseMultiStreamModule ):
    strDebugWindowName2 = "Video Monitor Right (or Bottom)"; # "DebugWindow"; # set to false to have no debug windows
    cv.NamedWindow( strDebugWindowName2, cv.CV_WINDOW_AUTOSIZE);
    if( nWantedResolution == k4VGA ):
        aWantedResolution = (1280, 960);    
    if( nWantedResolution == kVGA ):
        aWantedResolution = (640, 480);
    elif( nWantedResolution == kQVGA ):
        aWantedResolution = (320, 240);
    elif( nWantedResolution == kQQVGA ):
        aWantedResolution = (160, 120);
        
    if( bStereoMode ):
        cv.MoveWindow( strDebugWindowName2, aWantedResolution[0]+20, -1 );
    else:
        cv.MoveWindow( strDebugWindowName2, -1, aWantedResolution[1]+40 );


avd = ALProxy( "ALVideoDevice",  strNaoIp, 9559 );
strMyClientName = "nao_camera_viewer";
nFps = 30;
print( "INF: Camera subscribing: before..." );
if( not bUseMultiStreamModule ):
    strMyClientName = avd.subscribe( strMyClientName, nWantedResolution, nColorSpace, nFps );
    nUsedResolution = avd.getGVMResolution( strMyClientName );
else:
    strMyClientName = avd.subscribeCameras( strMyClientName, [0,1], [nWantedResolution,nWantedResolution], [nColorSpace,nColorSpace], nFps );
    nUsedResolution, nDumb = avd.getResolutions( strMyClientName );
#avd.setResolution( strMyClientName, 2);

print( "INF: Camera subscribing: after" );

nSizeX, nSizeY = avd.resolutionToSizes( nUsedResolution );
print( "GVM has Image properties: %dx%d" % (nSizeX,nSizeY) );
nNbrColorPlanes = 3;
if( nColorSpace == kGrey ):
    nNbrColorPlanes = 1;
bufferImageToDraw = cv.CreateImage( (nSizeX, nSizeY), cv.IPL_DEPTH_8U, nNbrColorPlanes );
if( bUseMultiStreamModule ):
    bufferImageToDraw2 = cv.CreateImage( (nSizeX, nSizeY), cv.IPL_DEPTH_8U, nNbrColorPlanes );
#print( dir( bufferImageToDraw ) );
#print( "channel: " + str( bufferImageToDraw.channel ) );

for i in range(len(anVFlipCamera) ):
    avd.setParam( kSelectCamera, i );
    avd.setParam( kFlipV, anVFlipCamera[i] );
    avd.setParam( kFlipH, anHFlipCamera[i] );
avd.setParam( kSelectCamera, nCameraToUse ); # change camera

#~ avd.setParam( kCameraAutoExpositionID, 0 );
#~ avd.setParam( 6, 255 );
#~ avd.setParam( 17, 512 );

#~ setCameraParamForRedAndBlue(False); # reset camera
#~ setCameraParamForRedAndBlue();

bKeyPressed = False;
nCptFrame = 0;
nCptImageSaved = 0;
timeBegin = time.time();
bSaveFrame = False;
bRecordMode = False;
bTestFrame = False;
bSaveStereoFrame = False;
nSaveStereoFramePass = 0;
bChangeCamera = False;
nShowProcessed = 0; # 0: show source, other value: show steps
work = cv.CreateImage( cv.GetSize(bufferImageToDraw), cv.IPL_DEPTH_8U, 3 );

bDrawInfo = True;
bDrawInfo = 0;
rLastComputedFps = 0;
bBlinkOn = False;

if( bDrawInfo ):
    nThickness = 1;
    font = cv.InitFont( cv.CV_FONT_HERSHEY_SIMPLEX, 0.5, 0.5, 0, nThickness, 8 );   
    
if( bMoveEyes ):
    import abcdk.config
    abcdk.config.bInChoregraphe = False; # access to the right proxy
    abcdk.config.strDefaultIP = strNaoIp;

    import abcdk.motiontools
    import abcdk.romeo
    abcdk.motiontools.eyesMover.setStiffness();
    abcdk.romeo.setCameraGroup( 1, bUseFuse = False );
    bEyesFlipFlop = True;
    for nNumCamera in range(2):
        avd.setParameter( nNumCamera, kCameraAutoExpositionID, 0 );
        avd.setParameter( nNumCamera, kCameraExposureID, 10 );
        avd.setParameter( nNumCamera, kCameraGainID, 511 );
        
if( bBlinkWhenSaving ):
    import abcdk.config
    abcdk.config.setDefaultIP( strNaoIp, True );
    import abcdk.leds

    
img_prev = None;
timeStampPrev = -1;
nCptExactTimeStamp = 0;
nCptExactTimeStampTotal = 0;
nCptRetrieve = 0;

while( not bKeyPressed ):
    nCptRetrieve += 1;
    if( False ):
        print( "camera current params:" );
        for i in range( 34 ):
            try:
                retVal = avd.getParam( i );
                print( "param %d: %s" % ( i, str( retVal ) ) );
            except BaseException, err:
                print( "DBG: get param(%d) => error: %s" % ( i, str( err ) ) );            
    #~ try:
    if( 1 ):
        if( not bUseMultiStreamModule ):
            dataImage = avd.getImageRemote( strMyClientName );
        else:
            #~ print( "getImagesRemote: avant" );
            dataImage = avd.getImagesRemote( strMyClientName );
            #~ print( "getImagesRemote: apres" );
        if( dataImage == None ):
            print( "ERR: dataImage is none!" );
        else:
            if( not bUseMultiStreamModule ):
                nSizeX = dataImage[0];
                nSizeY = dataImage[1];
                rTimeStamp = dataImage[4] + dataImage[5]/(1000000.);
                #~ print( "Image get: %dx%d" % (nSizeX,nSizeY) );
                #~ print( "Image prop: layer: %d, format: %d" % (dataImage[2],dataImage[3]) );
                image = dataImage[6];
                #~ print( "first char: '%s','%s','%s'" % ( image[0+960],image[1],image[2] )  );
                #~ print( "first char orded: %s,%s,%s" % ( ord( image[0] ), ord( image[1] ), ord( image[2] )  ) );
                # bufferImageToDraw.data = image;
            else:
                #~ print("image len: %d" % len(dataImage) );                
                if( dataImage[0] != 0 ):
                    nSizeX = dataImage[0][0]; # read only properties of image 1
                    nSizeY = dataImage[0][1];
                    rTimeStamp = dataImage[0][4] + dataImage[0][5]/(1000000.);
                if( len( dataImage ) > 2 ):
                    image = dataImage[2][nSizeX*nSizeY*3:];
                    image2 = dataImage[2];
                else:
                    # naoqi 2.0.2++
                    #~ print( "ERR: multistream: got an array but with no image(s)... dataImage: %s" % str(dataImage) );
                    #~ print( "ERR: multistream: got an array but with no image(s)... dataImage2: %s" % str(dataImage[1]) );
                    if( dataImage[0] != 0 ):
                        image = dataImage[0][6];
                    else:
                        image = None;
                        rTimeStamp = 0;
                    if( dataImage[1] != 0 ):
                        image2 = dataImage[1][6];
                        rTimeStamp2 = dataImage[1][4] + dataImage[1][5]/(1000000.);
                    else:
                        print( "ERR: multistream: second image is empty... (dataImage[1]: %s)" % str(dataImage[1]) );                        
                        image2 = None;
                        rTimeStamp2 = 0;
                if( image == None or image2 == None ):
                    print( "ERR: multistream: one or more image is None, im1: %s, im2: %s" % (image, image2) )
                    
            if( bDrawInfo ):
                if( not bUseMultiStreamModule ):
                    print( "- time stamp: %5.2f" % (rTimeStamp) );
                else:
                    print( "- time stamp: 1: %5.2f, 2: %5.2f" % (rTimeStamp, rTimeStamp2) );
                    
            # check stuffs
            
            if( bUseMultiStreamModule and abs(rTimeStamp-rTimeStamp2) > 0.001 ):
                print( "WRN: time stamp of image 2 has a difference of %sms (last was %d image(s) before, perfect (less than 1ms): %s%%)" % (int( (rTimeStamp2-rTimeStamp)*1000), nCptExactTimeStamp,int(round(nCptExactTimeStampTotal*100./nCptRetrieve))) );
                nCptExactTimeStamp = 0;
            else:
                nCptExactTimeStamp += 1;
                nCptExactTimeStampTotal += 1;
                
                
            if( timeStampPrev == rTimeStamp and rTimeStamp != 0 ):
                print( "WRN: time stamp of image, is same than previous! (%s)" % rTimeStamp );
            else:
                timeStampPrev = rTimeStamp;
            
            if( nColorSpace != kYUV422 ):
                # converted locally in NAO's  head
                cv.SetData( bufferImageToDraw, image );
                if( bUseMultiStreamModule ):
                    if( image2 != None ):
                        cv.SetData( bufferImageToDraw2, image2 );
            else:
                # manual burk convert from YUV
                #~ convertYUV_ToBGR( bufferImageToDraw, image, nSizeX, nSizeY );
                #~ if( bUseMultiStreamModule ):
                    #~ convertYUV_ToBGR( bufferImageToDraw2, image2, nSizeX, nSizeY );
                if( image != None ):
                    rgb = convertYUV_ToBGR_cv2( image, nSizeX, nSizeY );
                    cv.SetData( bufferImageToDraw, rgb );
                if( bUseMultiStreamModule ):
                    if( image2 != None ):
                        rgb2 = convertYUV_ToBGR_cv2( image2, nSizeX, nSizeY );
                        cv.SetData( bufferImageToDraw2, rgb2 );
                
            if( bTestFrame ):
                print( "Testing detection...\n");
                # test( bufferImageToDraw,  "D:\pythonscript\data\haarcascades\haarcascade_frontalface_alt.xml" );
                test( bufferImageToDraw,  "D:/Dev/dp/nao-detector/trainout5.xml" );
                bTestFrame = False;
            
            # test your own processing here...
            if( False ):
                retVal = findRedAndBlueMarks( bufferImageToDraw, work );
                x1,y1 = retVal[0];
                x2,y2 = retVal[1];
                dx = x2-x1;
                dy = y2-y1;            
                rDistToObject = math.sqrt( dx*dx+dy*dy );
                avgX = (x2+x1+1)/2; # round it!
                print( "rDistToObject: %f, avgX: %d" % (rDistToObject,avgX) ); # 47 pixels => 12cm; 25 pix => 23cm; 85px => 4cm
                # optimal position is 25, 126, en QQVGA, soit en VGA: 53, 252
                
            #~ if( True ):
                #~ import cv2
                #~ hist_item = cv2.calcHist(bufferImageToDraw,[0],None,[256],[0,256])
                #~ print hist;
                
            if( bDrawInfo ):
                colorText = (255,0,0);
                cv.PutText( bufferImageToDraw, "fps: %5.2f" % rLastComputedFps, (0,16), font, colorText );
                
            if( nShowProcessed == 0 ):
                cv.ShowImage( strDebugWindowName, bufferImageToDraw );
                if( bUseMultiStreamModule ):
                    cv.ShowImage( strDebugWindowName2, bufferImageToDraw2 );
            else:
                pass
                if( nShowProcessed == 1 ):
                    cv.ShowImage( strDebugWindowName, work );
                else:
                    cv.ShowImage( strDebugWindowName, work );
            nCptFrame +=1;

            if( not bUseMultiStreamModule ):
                if( bSaveStereoFrame or nSaveStereoFramePass != 0 ): # this block should be before bSaveFrame block
                    print( "Saving a stereo frame (pass:%d)!" % nSaveStereoFramePass );
                    if( nSaveStereoFramePass == 0 ):
                        avd.setParam( kSelectCamera,  nSaveStereoFramePass );
                        bSaveFrame = True;
                        nSaveStereoFramePass = 1;
                    elif( nSaveStereoFramePass == 1 ):
                        avd.setParam( kSelectCamera,  nSaveStereoFramePass );
                        bSaveFrame = True;
                        nSaveStereoFramePass = 0;
                        bSaveStereoFrame = False;
            else:
                if( bSaveStereoFrame ):
                    strTime = "_%5.2f" % time.time();
                    strTime = strTime.replace( ".", "_" );                    
                    strFilename = "camera_viewer_%04d_%s.png" % ( nCptImageSaved, strTime);
                    strFilenameL = strFilename.replace( ".p", "_l.p" );
                    strFilenameR = strFilename.replace( ".p", "_r.p" );
                    if( not bRomeoMode ):
                        led.fade( "AllLeds", 1., 0.2 );
                    print( "Saving image to %s" % strFilenameL );                    
                    cv.SaveImage( strFilenameL, bufferImageToDraw );
                    print( "Saving image to %s" % strFilenameR );                    
                    cv.SaveImage( strFilenameR, bufferImageToDraw2 );
                    
                    
            bSaveFrame = bSaveFrame or mem.getData( "Device/SubDeviceList/Head/Touch/Front/Sensor/Value" ) > 0.5;                    
            if( bSaveFrame ):
                strTime = "";
                if( bOutputTimeStampToFilename ):
                    strTime = "_%5.2f" % time.time();
                    strTime = strTime.replace( ".", "_" );
                strFilename = "camera_viewer_%d_%s_%04d.png" % ( avd.getParam(kSelectCamera),  strTime, nCptImageSaved );
                if( bRecordMode ):
                    strFilename = strFilename.replace( ".png", ".jpg" );
                    strFilename = "/tmp/recorded_images/" + strFilename;
                bSkip = False;
                if( bRecordMode ): 
                    if( 0 ):
                        # skip not moving image
                        img_numpy = numpy.frombuffer( image, dtype=numpy.uint8 );
                        if( img_prev != None ):
                            # compute diff in image
                            diff = cv2.absdiff( img_numpy, img_prev );
                            nMaxDiff = diff.max();
                            rMean = numpy.mean( diff );
                            print( "INF: max diff: %s, mean: %s" % (nMaxDiff, rMean) );
                            if( rMean <= 1.85 ): # 1.6 # 2.6 isn't enough for mouth moving!
                                bSkip = True;
                        img_prev = copy.deepcopy(img_numpy);
                        
                if( not bSkip ): 
                    print( "Saving image to %s" % strFilename );                    
                    if( not bRecordMode and not bRomeoMode ): led.fade( "AllLeds", 1., 0.2 );
                    cv.SaveImage( strFilename, bufferImageToDraw );
                    if( not bRecordMode and not bRomeoMode ): led.fade( "AllLeds", 0., 0.1 );
                    bSaveFrame = False;
                    nCptImageSaved += 1;
                    if( bBlinkWhenSaving and not bRomeoMode ):
                        # make leds blinking
                        if( (nCptImageSaved & 0x0f ) == 0x0f ):
                            # blink it!
                            if( bBlinkOn ):
                                nColor = 0x0;
                            else:                    
                                nColor = 0xFF0080;
                            bBlinkOn = not bBlinkOn;
                            abcdk.leds.dcmMethod.setEyesOneLed( nIndex=7, rTime=0.1, nColor = nColor, nEyesMask = 0x3 );
                        
                        
            if( bChangeCamera ):
                avd.setParam(kSelectCamera, (avd.getParam(kSelectCamera)+1)%2);
                bChangeCamera = False;
                
            if( nCptFrame == 10 ):
                rDuration = time.time() - timeBegin;
                rLastComputedFps = 10/rDuration;
                print( "fps: %f" % (rLastComputedFps) );
                nCptFrame = 0;
                timeBegin = time.time();
    #~ except BaseException, err:
        #~ print( "ERR: camera_viewer: (err:%s)" % (str(err)) );
        
    nKey =  cv.WaitKey(1) & 0xFF;
    bKeyPressed = ( nKey == ord( 'q' ) or nKey == ord( 'Q' ) );
    bSaveFrame = ( nKey == ord( 's' ) );
    bSaveStereoFrame = ( nKey == ord( 'S' ) );
    bToggleRecordMode = ( nKey == ord( 'r' ) );    
    bTestFrame = ( nKey == ord( 't' ) );
    bChangeCamera = ( nKey == ord( 'c' ) );
    if( nKey == ord( 'p' ) ):
        nShowProcessed = ( nShowProcessed + 1 ) % 4 ;
        
    if( bToggleRecordMode ):
        bRecordMode = not bRecordMode;
        print( "Record all frame: %s" % bRecordMode );
        try: os.makedirs( "/tmp/recorded_images/" )
        except: pass
    if( bRecordMode ):
        bSaveFrame = True;
        bOutputTimeStampToFilename = True;
        
    if( bMoveEyes ):
        import abcdk.config
        abcdk.config.bInChoregraphe = False; # access to the right proxy
        abcdk.config.strDefaultIP = strNaoIp;
        
        import abcdk.motiontools
        bEyesFlipFlop = not bEyesFlipFlop;
        if( bEyesFlipFlop ):
            nSide = -0.1;
        else:
            nSide = +0.1;
        abcdk.motiontools.eyesMover.moveLeft( [nSide,0.], 0.1, bWaitEnd = False );
# while - end
cv.SaveImage( "camera_viewer_at_exit.png", bufferImageToDraw ); # save last image at quit


print("Unsubscribing..." );
avd.unsubscribe( strMyClientName );
