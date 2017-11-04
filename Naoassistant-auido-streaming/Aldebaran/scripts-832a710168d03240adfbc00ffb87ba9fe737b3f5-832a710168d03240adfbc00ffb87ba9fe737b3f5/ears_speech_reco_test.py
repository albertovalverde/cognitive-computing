# -*- coding: utf-8 -*-

###########################################################
# Audio File Tools
# Author A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved
###########################################################

import os
import time

def getTheoricResultsFromFilename( strFilename ):
    """
    extract theoric result from a hand tagged filename
    eg: "test_01_cc_alastair__at_what_time_is_breakfast.wav" => at what time is breakfast
    """
    txt = strFilename.replace("_2.", "." ).split(".")[0].split("__")[-1].replace("_", " ") # (ugly line)
    return txt.lower()
    
def isTheoricResultsGood( strFilename, strRecognizedText ):
    """
    Return a matching ratio 0..1
    """
    strTheoricText = getTheoricResultsFromFilename(strFilename)
    strRecognizedTextCleaned = strRecognizedText.strip( "?!?.-").lower()
    print( "DBG: isTheoricResultsGood: comparing '%s' and '%s'" % ( strRecognizedTextCleaned, strTheoricText ) )
    bIsSub = strRecognizedTextCleaned in strTheoricText
    if not bIsSub:
        return 0.
    rLenRatio = len(strRecognizedTextCleaned) / float(len(strTheoricText))
    print( "DBG: isTheoricResultsGood: rLenRatio: %s" % rLenRatio )
    bIsQuiteSameLength = abs(1 - rLenRatio ) < 0.15
    return bIsSub and bIsQuiteSameLength
    
def getTheoricResultsMatchingRatio( strFilename, strRecognizedText ):
    """
    Return a matching ratio 0..1
    """
    strTheoricText = getTheoricResultsFromFilename(strFilename)
    strRecognizedTextCleaned = strRecognizedText.strip( "?!?.").replace("-", "" ).lower()
    print( "DBG: getTheoricResultsMatchingRatio: comparing '%s' and '%s'" % ( strRecognizedTextCleaned, strTheoricText ) )
    bIsSub = strRecognizedTextCleaned in strTheoricText
    if not bIsSub:
        return 0.
    rLenRatio = len(strRecognizedTextCleaned) / float(len(strTheoricText))
    print( "DBG: getTheoricResultsMatchingRatio: rLenRatio: %s" % rLenRatio )
    if rLenRatio > 1.:
        rLenRatio = 1 - (1.2-1)
    return rLenRatio
    
def getTheoricResultsMatchingRatioPhonetic( strFilename, strRecognizedText ):
    """
    Return a matching ratio 0..1
    """
    import abcdk.metaphone
    import abcdk.stringtools
    strTheoricText = getTheoricResultsFromFilename(strFilename)
    strRecognizedText = strRecognizedText.strip( "?!?.").replace("-", "" ).lower()
    print( "DBG: getTheoricResultsMatchingRatioPhonetic: comparing '%s' and '%s'" % ( strRecognizedText, strTheoricText ) )

    # direct matching
    if( strRecognizedText == strTheoricText ):
        print( "DBG: reco: direct match: '%s' '%s'" % (strRecognizedText,strTheoricText) );
        return 1.

    metaReco = abcdk.metaphone.dm(unicode( strRecognizedText ) );
    if( len(metaReco[0]) < 1 ):        
        return 0.
        
    metaTheo = abcdk.metaphone.dm(unicode(strTheoricText));
    print( "DBG: reco: (%s) comp to theo: (%s)" % (metaReco,metaTheo) );
    if( metaReco == metaTheo ):
        print( "INF: metaphone match: %s ~= %s" % ( strRecognizedText, strTheoricText ) );
        return 0.9421 # magic just to know how match has been made
        
    # compute distance
    rMidLen = ( len(metaReco[0]) + len( metaTheo[0] ) ) / 2;
    rDist = abcdk.stringtools.levenshtein( metaReco[0], metaTheo[0] ) / float(rMidLen);
    rConfidence = 0.9 - rDist # TODO: why ('AL', 'ALF') (yellow) comp to ('HL', '') (hello) give a distance of 0 ?
    print( "DBG: rMidLen: %s, rDist: %s, rConfidence: %s" % (rMidLen, rDist,rConfidence) )
    return rConfidence
# getTheoricResultsMatchingRatioPhonetic - end    




def recognizeUsingOneChannel( strFileIn, nIdxChannelToUse = 3 ):
    """
    return recognized text or None if no recognition or False on error
    - nIdxChannelToUse: channel to use. If mono file, this parameters won't be used
    """
    import abcdk.sound
    import abcdk.freespeech
    strDst = strFileIn.split("/")[-1]
    strDst = strDst.replace( ".wav", "_mono.wav" )
    strFullDst = "/tmp/" + strDst
    print( "\n\nINF: Testing %s" % strFileIn )    
    bRet = abcdk.sound.convertToOneChannel( strFileIn, strFullDst, nIdxChannelToUse )
    if not bRet:
        return False
    timeBegin = time.time()
    retVal = abcdk.freespeech.freeSpeech.analyse( strFullDst )
    rProcessDuration = time.time() - timeBegin
    print( "INF: ret: %s (process duration:%s)" % (retVal, rProcessDuration) )
    return retVal
# recognizeUsingOneChannel - end  

def testAllFilesOneChannel( strPath, nIdxChannelToUse = 3 ):
    """
    2016/10/27: result on first files:
        channel 3: success/try: 13/58 (  0.2%) (sumConfidence: 12.42, avg:  0.96)
        channel 2: success/try: 17/58 (  0.3%) (sumConfidence: 16.26, avg:  0.96)
        channel 0: success/try: 12/58 (  0.2%) (sumConfidence: 11.76, avg:  0.98)
        
        channel 2: success/try: 48/226 (  0.2%) (sumConfidence: 46.78, avg:  0.97)        
        channel 0: success/try: 32/226 (  0.1%) (sumConfidence: 31.48, avg:  0.98)
    """
    nNbrTry = nNbrSuccess = 0
    rSumMatching = 0.
    listAllResults = [] # filename, waited, recognized, ratio match
    print( "INF: testAllFilesOneChannel on path '%s', channel to use: %d" % (strPath, nIdxChannelToUse) )
    for file in sorted(os.listdir(strPath)):
        if not ".wav" in file:
            continue
        nNbrTry += 1
        strRecognized = recognizeUsingOneChannel( strPath + file, nIdxChannelToUse=nIdxChannelToUse )
        if strRecognized != None:
            rRatio = getTheoricResultsMatchingRatioPhonetic( file, strRecognized )
            listAllResults.append( [file, getTheoricResultsFromFilename(file), strRecognized, rRatio ] )
            if  rRatio > 0.72:
                rSumMatching += rRatio
                print( "INF: SUCCESS !" )
                nNbrSuccess += 1
        if nNbrTry > 3 and 0:
            break
    if nNbrTry > 0:        
        print( "\nTestAllFilesOneChannel: channel %d: success/try: %s/%s (%5.1f%%) (sumConfidence: %5.2f, avg: %5.2f)" % (nIdxChannelToUse, nNbrSuccess,nNbrTry,nNbrSuccess/float(nNbrTry), rSumMatching, rSumMatching/nNbrSuccess) )
        for res in listAllResults:
            print( "%30s, %20s, %20s, (%5.2f)" % (res[0], res[1], res[2], res[3]) )
    else:
        print( "\nERR: TestAllFilesOneChannel: no files found !!!" )
    print("\n")
# testAllFilesOneChannel - end


def autoTest():
    assert( getTheoricResultsFromFilename("test_01_cc_alastair__at_what_time_is_breakfast_2.wav") == "at what time is breakfast" )
    assert( isTheoricResultsGood("test_01_cc_alastair__at_what_time_is_breakfast.wav" , "at what time is breakfast?" ) )
    assert( getTheoricResultsMatchingRatioPhonetic( "bye.wav", "buy" ) == 0.9421 )
    assert( getTheoricResultsMatchingRatioPhonetic( "at what time is breakfast.wav", "at what time is breakfast?" ) > 0.94 )
    assert( getTheoricResultsMatchingRatioPhonetic( "can i have access to the wifi.wav", "can I have access to the Wi-Fi?" ) > 0.99 )
    


def testPerfAllFile_OneChannel():
    strPath = "/home/likewise-open/ALDEBARAN/amazel/Bureau/sound_recording_sound/ears_test_recording/cleaned_test_sound/"
    nNbrChannelToTest = 14
    #strPath = "/tmp/cleaned_test_sound/"
    #recognizeUsingOneChannel( strPath + "test_01_cc_alastair__at_what_time_is_breakfast.wav" )
    strPath = "/home/likewise-open/ALDEBARAN/amazel/dev/git/ears_benchmark_i/audio_enhancement_measurement/20161202_EARS_demo_enhancement/"
    nNbrChannelToTest = 1
    for nNumChannel in range(nNbrChannelToTest):
        testAllFilesOneChannel( strPath, nNumChannel )
        
if( __name__ == "__main__" ):
    autoTest();
    testPerfAllFile_OneChannel()
    
