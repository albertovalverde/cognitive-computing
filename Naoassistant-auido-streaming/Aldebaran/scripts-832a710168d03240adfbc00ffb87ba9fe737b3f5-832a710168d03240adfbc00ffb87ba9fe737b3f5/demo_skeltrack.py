from naoqi import ALProxy
import csv
import sys
import time
import numpy as np
import cv2
import cv2.cv as cv
import math
import cProfile
import pstats
import copy
import scipy.signal as signal


class bufferedImage(object):
    def __init__(self,anReducedBuffer,nDimReduction,nReducedWidth,nReducedHeight,nWidth,nHeight):
        self.anReducedBuffer = anReducedBuffer
        self.nReducedWidth = nReducedWidth
        self.nReducedHeight = nReducedHeight
        self.nWidth = nWidth
        self.nHeight = nHeight
        self.nDimReduction = nDimReduction

def medianFilter (aImage, nWindowHeight, nWindowWidth):
    nSize = aImage.nReducedWidth * aImage.nReducedHeight
    aTmpBuffer = [0 for i in range(0,nSize)]

    nEdgeX = nWindowWidth / 2;
    nEdgeY = nWindowWidth / 2;

    for nI in range(nEdgeY,aImage.nReducedHeight - nEdgeY):
        for nJ in range( nEdgeX, aImage.nReducedWidth - nEdgeX):
            aWindowContent = []
            for nWindowI in range(0, nWindowHeight):
                for nWindowJ in range(0 , nWindowWidth):
                    nIndex = ((nI + nWindowI - nEdgeY) * aImage.nReducedWidth) + (nJ + nWindowJ - nEdgeX);
                    aWindowContent.append(aImage.anReducedBuffer[nIndex]);
            aWindowContent.sort()
            aTmpBuffer[(nI*aImage.nReducedWidth) + nJ] = aWindowContent[nWindowWidth * nWindowHeight /2];


	#copy of the result in aImage
    for nI in range(nEdgeY, aImage.nReducedHeight - nEdgeY):
        for nJ in range(nEdgeX, aImage.nReducedWidth - nEdgeX):
            nIndex = (nI*aImage.nReducedWidth) + nJ;
            aImage.anReducedBuffer[nIndex] = aTmpBuffer[nIndex];

def processingPixel(nValue,nThresholdBegin,nThresholdEnd):
    #print(str(nValue) + " " + str(nThresholdBegin) + " " + str(nThresholdEnd))
    if (nValue < nThresholdBegin or nValue > nThresholdEnd):
        return 0.0
    else:
        return float(nValue)

def processBuffer (aImage,nWidth,nHeight,nDimensionFactor,nThresholdBegin,nThresholdEnd):
    nReducedWidth = (nWidth - nWidth % nDimensionFactor) / nDimensionFactor
    nReducedHeight = (nHeight - nHeight % nDimensionFactor) / nDimensionFactor

    nReducedSize = nReducedWidth * nReducedHeight
    anReducedBuffer = [0 for i in range(nReducedSize)]

    for nI in range (0, nReducedWidth):
        for nJ in range(0, nReducedHeight):
            nIndex = nJ * nWidth * nDimensionFactor + nI * nDimensionFactor;
            nValue = int(aImage[nIndex]);

            if (nValue < nThresholdBegin or nValue > nThresholdEnd):
                anReducedBuffer[nJ * nReducedWidth + nI] = 0;
                continue

            anReducedBuffer[nJ * nReducedWidth + nI] = nValue;

    toReturn = bufferedImage(anReducedBuffer,nDimensionFactor,nReducedWidth,nReducedHeight,nWidth,nHeight)
    return toReturn;

def grayingPixel(nValue):
    if int(nValue) != 0 :
        return 0
    else:
        return 255

def createGrayscaleBuffer (image):
    nSize = image.nWidth * image.nHeight
    anGrayscaleBuffer = [255 for i in range(nSize)]

    for i in range(0,image.nReducedWidth):
        for j in range(0,image.nReducedHeight):
            if image.anReducedBuffer[j * image.nReducedWidth + i] !=0:
                normedVal = 0;
                index = j * image.nDimReduction * image.nWidth + i * image.nDimReduction
                anGrayscaleBuffer[index] = int(normedVal);

    return anGrayscaleBuffer


def displaySkeleton(aListJoints,bufferImageToDraw):
    thickness = -1;
    lineType = 8;

    head = aListJoints[0]
    leftHand = aListJoints[1]
    rightHand = aListJoints[2]
    leftShoulder = aListJoints[3]
    rightShoulder = aListJoints[4]
    leftElbow = aListJoints[5]
    rightElbow = aListJoints[6]

    bHead = False
    bLeftHand = False
    bRightHand = False
    bLeftShoulder = False
    bRightShoulder = False
    bLeftElbow = False
    bRightElbow = False

    if (head[0] != -1) and (head[1] != -1):
        cv2.circle(bufferImageToDraw,(head[0],head[1]),10,(0,255,0),thickness,lineType)
        bHead = True

    if (leftHand[0] != -1) and (leftHand[1] != -1):
        cv2.circle(bufferImageToDraw,(leftHand[0],leftHand[1]),10,(255,0,0),thickness,lineType)
        bLeftHand = True

    if (rightHand[0] != -1) and (rightHand[1] != -1):
        cv2.circle(bufferImageToDraw,(rightHand[0],rightHand[1]),10,(0,0,255),thickness,lineType)
        bRightHand = True

    if (leftShoulder[0] != -1) and (leftShoulder[1] != -1):
        cv2.circle(bufferImageToDraw,(leftShoulder[0],leftShoulder[1]),10,(15,175,25),thickness,lineType)
        bLeftShoulder = True

    if (rightShoulder[0] != -1) and (rightShoulder[1] != -1):
        cv2.circle(bufferImageToDraw,(rightShoulder[0],rightShoulder[1]),10,(15,175,25),thickness,lineType)
        bRightShoulder = True

    if (leftElbow[0] != -1) and (leftElbow[1] != -1):
        cv2.circle(bufferImageToDraw,(leftElbow[0],leftElbow[1]),10,(240,175,25),thickness,lineType)
        bLeftElbow = True

    if (rightElbow[0] != -1) and (rightElbow[1] != -1):
        cv2.circle(bufferImageToDraw,(rightElbow[0],rightElbow[1]),10,(240,175,25),thickness,lineType)
        bRightElbow = True

	
    bNeckPointComputed = False
    neckPoint = None
    if bHead == True and bLeftShoulder == True and bRightShoulder == True:
        nX = head[0]
        nY = int((leftShoulder[1] + rightShoulder[1]) / 2.0)
        neckPoint = (nX,nY)
        bNeckPointComputed = True;

	if bNeckPointComputed == True:
		cv2.line(bufferImageToDraw,(head[0],head[1]),neckPoint,(0,43,255),2);
		cv2.line(bufferImageToDraw,neckPoint,(rightShoulder[0],rightShoulder[1]),(0,43,255),2);
		cv2.line(bufferImageToDraw,neckPoint,(leftShoulder[0],leftShoulder[1]),(0,43,255),2);

    else:
        if bHead == True and bLeftShoulder == True:
            cv2.line(bufferImageToDraw,(head[0],head[1]),(leftShoulder[0],leftShoulder[1]),(0,43,255),2);

        if bHead == True and bRightShoulder == True:
            cv2.line(bufferImageToDraw,(head[0],head[1]),(rightShoulder[0],rightShoulder[1]),(0,43,255),2);

    if bLeftShoulder == True and bLeftElbow == True:
        cv2.line(bufferImageToDraw,(leftShoulder[0],leftShoulder[1]),(leftElbow[0],leftElbow[1]),(0,43,255),2);

    if bRightShoulder  == True and bRightElbow  == True:
        cv2.line(bufferImageToDraw,(rightShoulder[0],rightShoulder[1]),(rightElbow[0],rightElbow[1]),(0,43,255),2);

    if bLeftElbow  == True and bLeftHand  == True:
        cv2.line(bufferImageToDraw,(leftElbow[0],leftElbow[1]),(leftHand[0],leftHand[1]),(0,43,255),2);

    if bRightElbow  == True and bRightHand  == True:
        cv2.line(bufferImageToDraw,(rightElbow[0],rightElbow[1]),(rightHand[0],rightHand[1]),(0,43,255),2);


def helloDetector(aListJoints,anXPoses,tts):
    leftHand = aListJoints[1]
    rightHand = aListJoints[2]
    leftShoulder = aListJoints[3]
    rightShoulder = aListJoints[4]

    bLeftHand = False
    bRightHand = False
    bLeftShoulder = False
    bRightShoulder = False

    if (leftHand[0] != -1) and (leftHand[1] != -1):
        bLeftHand = True

    if (rightHand[0] != -1) and (rightHand[1] != -1):
        bRightHand = True

    if (leftShoulder[0] != -1) and (leftShoulder[1] != -1):
        bLeftShoulder = True

    if (rightShoulder[0] != -1) and (rightShoulder[1] != -1):
        bRightShoulder = True

    if bRightHand == True and bRightShoulder == True:
        if rightHand[1] < (rightShoulder[1] - 40):
            anXPoses.append(rightHand[0]);
            if len(anXPoses) > 3:
                anXPoses.pop(0)


            if len(anXPoses) == 3:
                biggestDiff = 0
                for i in range(len(anXPoses)):
                    for j in range(i+1 , len(anXPoses)):
                        diff = math.fabs(anXPoses[i] - anXPoses[j])
                        if diff > biggestDiff:
                            biggestDiff = diff;

                if biggestDiff > 15 :
                    return "hello"
                else:
                    return "right"
            else:
                return "right"
        else:
            del anXPoses[:]

    if bLeftHand == True and bLeftShoulder == True:
        if leftHand[1] < (leftShoulder[1] - 40):
            return "left"

def getJoints(skeltrackProxy,image):
    #listJoints = skeltrackProxy.trackJoints(list(image.anReducedBuffer),image.nReducedWidth,image.nReducedHeight) 
    listJoints = skeltrackProxy.trackJoints(image.anReducedBuffer,image.nReducedWidth,image.nReducedHeight) 
    return listJoints

def mainVideo():
    robotIP = "10.0.204.119"
    strId = "skel_" + str(time.time())
    strDebugWindowName = "Debug skeltrack"

    tts = ALProxy ("ALTextToSpeech", robotIP, 9559)
    video = ALProxy("ALVideoDevice",robotIP,9559)
    status = video.subscribeCamera(strId,2,1,23,10)

    if status == "":
        raise Exception("subscribtion to camera failed")
    else:
        strId = status

    nUsedResolution = video.getResolution( strId );
    nWidth, nHeight = video.resolutionToSizes( nUsedResolution );

    bufferImageToDraw = cv.CreateImage( (nWidth, nHeight), cv.IPL_DEPTH_8U, 3 );

    cv.NamedWindow( strDebugWindowName, cv.CV_WINDOW_NORMAL );
    cv2.moveWindow( strDebugWindowName, 0, 0 );
    cv2.resizeWindow( strDebugWindowName, 640, 480 );

    #tts.say("\\RSPD=95\\ Waiting for a human !")

    try:
        skeltrackProxy = ALProxy("ALSkeletonDetector", robotIP, 9559)
    except Exception, e:
        print "Error was: ", e
        raise Exception("Could not create proxy to ALSkeletonDetector")

    anXPoses = []
    running = True
    step = "hello"
    while running == True:
        dataImage = video.getImageRemote(strId)
        if dataImage == None:
            raise Exception("Could not get a valid image")
        original = np.fromstring( dataImage[6], dtype=np.uint16 );

        nDimensionFactor = 2
        nThresholdBegin = 500
        nThresholdEnd = 1700

        original = original.reshape(nHeight,nWidth)

        #get one pixel every nDimensionFactor^th pixel
        tmp = copy.copy(original)
        tmp = tmp[::nDimensionFactor,::nDimensionFactor]

        #apply the thresholding on every values
        f = np.vectorize(processingPixel)
        tmp = f(tmp,nThresholdBegin,nThresholdEnd)

        #apply the medianBlur
        tmp = signal.medfilt2d(tmp,(3,3))

        nReducedWidth = (nWidth - nWidth % nDimensionFactor) / nDimensionFactor
        nReducedHeight = (nHeight - nHeight % nDimensionFactor) / nDimensionFactor
        tmp = tmp.reshape(1,nReducedWidth*nReducedHeight)[0]
        tmp = bufferedImage(tmp.tolist(),2,nReducedWidth,nReducedHeight,nWidth,nHeight)

        try:
            #listJoints = skeltrackProxy.trackJoints(list(image.anReducedBuffer),image.nReducedWidth,image.nReducedHeight) 
            listJoints = getJoints(skeltrackProxy,tmp)
            pass
        except RuntimeError as err:
            print ("error: ", format(err))

        detected = "none"
        if(len(listJoints)>0):
            detected = helloDetector(listJoints,anXPoses,tts)
        if (step == "hello") and (detected == "hello"):
            tts.say("\\RSPD=95\\ Hello human.  \\PAU=1000\\ It's time to do some gym !")
            tts.say("\\RSPD=95\\  Raise your right arm !")
            step = "right"
        elif (step == "right") and (detected == "left"):
            tts.say("\\RSPD=95\\ Your right arm please")
        elif (step == "right") and (detected == "right"):
            tts.say("\\RSPD=95\\ Raise  your left arm !")
            step = "left"
        elif (step == "left") and (detected == "right"):
            tts.say("\\RSPD=95\\ Your left arm please")
        elif (step == "left") and (detected == "left"):
            tts.say("\\RSPD=95\\ Wow, great !\\PAU=500\\  See you later sporty man.")
            step = "none"

        #grayscale = createGrayscaleBuffer(image);

        grayscale = copy.copy(original)
        #grayscale = grayscale.reshape(nHeight,nWidth)

        grayscale[::nDimensionFactor,::nDimensionFactor] = 0

        f = np.vectorize(processingPixel)
        grayscale = f(grayscale,nThresholdBegin,nThresholdEnd)
        f = np.vectorize(grayingPixel)
        grayscale = f(grayscale)
        grayscale = grayscale.astype(np.uint8)
        
        bufferImageToDraw = cv2.cvtColor(grayscale,cv.CV_GRAY2RGB)
        bufferImageToDraw = np.reshape(bufferImageToDraw, (nHeight, nWidth,3))
        if(len(listJoints) > 0):
            displaySkeleton(listJoints,bufferImageToDraw)
        cv.ShowImage( strDebugWindowName, cv.fromarray(bufferImageToDraw) )
        nKey =  cv.WaitKey(1);

        if nKey != -1 and nKey < 255:
            if chr(nKey) == 'q':
                running = False

def mainSnapshot():
    #robotIP = "127.0.0.1"
    robotIP = "10.0.204.119"
    try:
        skeltrackProxy = ALProxy("SkeltrackService", robotIP, 9559)
    except Exception, e:
        print "Error was: ", e
        raise Exception("Could not create proxy to SkeltrackService")

    doc = []
    with open('snapshot-twoUp.txt') as csvfile:
        shapereader = csv.reader(csvfile, delimiter=' ')
        firstLine = True
        maxX = 0
        maxY = 0
        for row in shapereader:
            if firstLine == True:
                firstLine = False
                maxY = float(row[0])
                maxX = float(row[1])
            else:
                for elem in row:
                    if elem != '':
                        if (float(elem) > 500) and (float(elem) < 2200):
                            doc.append(int(elem))
                        else:
                            doc.append(0)


    nDimensionFactor = 2
    nThresholdBegin = 500
    nThresholdEnd = 1700
    nWidth = 320
    nHeight = 240


    #image = processBuffer(doc,nWidth,nHeight,nDimensionFactor,nThresholdBegin,nThresholdEnd)

    #get one pixel every nDimensionFactor^th pixel
    tmp = np.array(doc,dtype=np.float32)
    tmp = tmp.reshape(nHeight,nWidth)
    tmp = tmp[::nDimensionFactor,::nDimensionFactor]

    #apply the thresholding on every values
    f = np.vectorize(processingPixel)
    tmp = f(tmp,nThresholdBegin,nThresholdEnd)

    #apply the medianBlur
    tmp = signal.medfilt2d(tmp,(3,3))

    nReducedWidth = (nWidth - nWidth % nDimensionFactor) / nDimensionFactor
    nReducedHeight = (nHeight - nHeight % nDimensionFactor) / nDimensionFactor
    image = tmp.reshape(1,nReducedWidth*nReducedHeight)[0]
    image = bufferedImage(image.tolist(),2,nReducedWidth,nReducedHeight,nWidth,nHeight)

    try:
        stuff = getJoints(skeltrackProxy,image)
    except RuntimeError as err:
        print ("error: ", format(err))

if __name__ == "__main__":
    cProfile.run("mainVideo()","skel_stat")
#    cProfile.run("mainSnapshot()","skel_stat")
#    p = pstats.Stats("skel_stat") 
#    p.strip_dirs().sort_stats(2).print_stats()

