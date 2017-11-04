# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Body Talk Tools
# Author A. Mazel
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Body Talk Tools: tracking and prepare to interaction functions"

print( "importing abcdk.bodytalk" );

import mutex
import random
import time

import arraytools
import config
import image
import leds
import motiontools
import naoqitools
import numeric
import poselibrary
import speech
import system
import test
import tracking # to use tracking initialisation, without copy/paste the code, but we won't use the tracking update method!

class BodyTalk:
    """
    Make the body moves, randomly related to some imaginated speech.
    Normal use:
        prepare() - put nao in a specific 'ready' position(optionnal)
        start()
        stop()
    """

    def __init__( self ):
        self.mutex = mutex.mutex(); # we armour init, pause and destroy
        self.bDebugMode = False;
        self.bPrepared = False;
        self.bRunning = False;
        self.bStanding = True;
        self.motion_id_head = -1;        
        self.motion_id_arms = -1;
        self.motion_id_legs = -1;
        
        self.motion = None;
        self.leds = None;
        self.mem = None;
        
        self.bUseHead = True; # do we send movement to head ?
        self.bTrackFace = False;
        self.timeLastUpdateTestRandom = 0;
        
        self.rFaceSide = 0.;
        self.rFaceElevation = 0.;        
        self.timeLastSeen = 0;
        self.aLastHeadAngle = [0.]*2; # we notice then angle of last send, so the head is refresh asap if angle change a lot
        
        #self.strFaceDetectMemoryName = "extractors/HaarExtractor/detected";
        self.strFaceDetectMemoryName = "FaceDetection/FaceDetected";
        self.strFacePositionMemoryName = "Tracking/FacePosition";
        
        
        self.nSayID = -1; # optionnal thread to watch for autostop
        self.tts = None;
        
        self.rFaceTrackTimeBeforeLostFace = 4.; # after this time, if we haven't see face, raz head to center
        
        self.bHasRightToUseLegs = True;
        self.bHasEyesLeds = True;
        self.bUseMouth = False;
        self.eyesMover = None;
        self.astrHeadPitch = ["HeadPitch","HeadPitch"];
        self.strHeadYaw = "HeadYaw";
        self.strShoulderPitch = "ShoulderPitch";        
        self.strShoulderRoll = "ShoulderRoll";
        if( system.isOnRomeo() ):
            self.bHasRightToUseLegs = False;
            self.bHasEyesLeds = False;
            self.bUseMouth = True;
            self.eyesMover = motiontools.eyesMover;
            # joint translation
            self.astrHeadPitch = ["HeadPitch","NeckPitch"];
            self.strHeadYaw = "NeckYaw";
            self.strShoulderPitch = "ShoulderPitch";        
            self.strShoulderRoll = "ShoulderYaw";
            
        
        self.rLastSide = 0.; # We store them for the stop method
        self.rLastElevation = 0.;
        
        self.loadMovement();
    # __init__ - end
    
    def initProxy( self ):
        # we don't want to do that at init because for some of autotest, the config isn't already set at init
        if( self.motion == None ):
            self.motion = naoqitools.myGetProxy( "ALMotion" );
            assert( self.motion != None );
        if( self.leds == None ):
            self.leds = naoqitools.myGetProxy( "ALLeds" );
            assert( self.leds != None );
        if( self.mem == None ):
            self.mem = naoqitools.myGetProxy( "ALMemory" );
            assert( self.mem != None );            
    # initProxy - end
    
    def patchHands( self, listAnimation ):
        rMultiplier = 57.3;
        for nNumAnim in range(len(listAnimation)):
            #~ for nIdxJoint in range( len(listAnimation[nNumAnim][0] ) ):
                #~ strJointName = listAnimation[nNumAnim][0][nIdxJoint];
                #~ if( "Hand" in strJointName ):
                    #~ for nNumKey in range( len( listAnimation[nNumAnim][2][nIdxJoint] ) ):
                        #~ listAnimation[nNumAnim][2][nIdxJoint][nNumKey][0] *= rMultiplier;
                        #~ print( "DBG: abcdk.BodyTalk.patchHands: new value is %f" % listAnimation[nNumAnim][2][nIdxJoint][nNumKey][0] );
            if( listAnimation[nNumAnim] != None ):
                listAnimation[nNumAnim] = motiontools.transformTimeline( listAnimation[nNumAnim][0], listAnimation[nNumAnim][1], listAnimation[nNumAnim][2], { "Hand": ["m", rMultiplier] } );
    # patchHands - end
    
    def loadMovement( self ):
        """
        Initialise ALL movements!
        """
        timeBegin = time.time();
        if( system.isOnRomeo() ):
            import bodytalk_movements_romeo as bodytalk_movements
        else:
            import bodytalk_movements
        # warning: the first animation could be None !
        self.movement_head_precalc = arraytools.dup( bodytalk_movements.head );
        self.movement_sit_arms_precalc = arraytools.dup( bodytalk_movements.sit );
        self.movement_stand_arms_precalc = arraytools.dup( bodytalk_movements.stand_arms );
        self.movement_stand_legs_precalc = arraytools.dup( bodytalk_movements.stand_legs );
        self.movement_stand_arms_table_precalc = arraytools.dup( bodytalk_movements.stand_arms_table );
        
        
        self.patchHands( self.movement_stand_arms_precalc );
        self.patchHands( self.movement_stand_arms_table_precalc );
        self.patchHands( self.movement_sit_arms_precalc );
        
        print( "INF: abcdk.BodyTalk.loadMovement in %f second(s)" % ( time.time() - timeBegin ) );
    # loadMovement - end
    
    def debug( self, strMessage ):
        if( self.bDebugMode ):
            print strMessage;
    # debug - end
    
    def getName( self ):
        return "abcdk.bodytalk";
        
    def detectPosition( self ):
        self.bStanding = ( motiontools.getCurrentPosture() == "Standing" or motiontools.getCurrentPosture() == "Crouching" ); # should works also when crouched, and because Romeo is often detected as crouched...
        if( self.bStanding == True ):            
            self.movement_arms_to_use_precalc = self.movement_stand_arms_precalc;
        else:
            self.movement_arms_to_use_precalc = self.movement_sit_arms_precalc;
        print( "INF: abcdk.BodyTalk.detectPosition: standing: %s" % str( self.bStanding ) );
        
    def computeMovementToUse( self, astrJointsToExclude = [], astrObstacles = [] ):
        """
        from the precalc movement, compute a specific set, handling joint disabling, soft calibration, obstacles...
        movement are taken from self.movement_xxx_precalc and stored to self.movement_xxx
        """
        self.detectPosition();
        
        self.movement_head = arraytools.dup( self.movement_head_precalc );
        self.movement_arms = arraytools.dup( self.movement_arms_to_use_precalc );
        self.movement_legs = arraytools.dup( self.movement_stand_legs_precalc );
        
        if( "Table" in astrObstacles ):
            print( "INF: abcdk.BodyTalk.computeMovementToUse: using obstacles 'Table' movements set" ); 
            self.movement_arms = arraytools.dup( self.movement_stand_arms_table_precalc );

        astrJointsToExclude = poselibrary.PoseLibrary.getListJoints( astrJointsToExclude );
        #~ print( "self.movement_head: %s" % self.movement_head );
        #~ print( "self.movement_arms: %s" % self.movement_arms );
        
        if( len(astrJointsToExclude) > 0 ):
            # joint exclusion
            print( "INF: abcdk.BodyTalk.computeMovementToUse: excluding those joint(s): %s" % astrJointsToExclude );
            
            print( "INF: abcdk.BodyTalk.computeMovementToUse: processing head movements: " );
            for i in range( len( self.movement_head ) ):
                motiontools.filterTimeline( self.movement_head[i], astrJointsToExclude );
                
            print( "INF: abcdk.BodyTalk.computeMovementToUse: processing arms movements: " );            
            for i in range( len( self.movement_arms ) ):
                motiontools.filterTimeline( self.movement_arms[i], astrJointsToExclude );
                
            print( "INF: abcdk.BodyTalk.computeMovementToUse: processing legs movements: " );
            for i in range( len( self.movement_legs ) ):
                motiontools.filterTimeline( self.movement_legs[i], astrJointsToExclude );
                
        #~ print( "self.movement_head: %s" % self.movement_head );
        #~ print( "self.movement_arms: %s" % self.movement_arms );
    # computeMovementToUse - end
        
    
    def prepare( self, bUseHead = True, rSide = 0., rElevation = 0., bTrackFace = False, astrJointsToExclude = [], astrObstacles = [] ):
        """
        Prepare to speak (optionnal)
        """
        while( self.mutex.testandset() == False ):
            print( "INF: abcdk.BodyTalk.prepare: already initing, waiting..." );
            time.sleep( 0.1 );        
        self.debug( "DBG: abcdk.BodyTalk.prepare: in..." );        
        if( self.bPrepared ):
            self.mutex.unlock();
            return;
        self.bPrepared = True;
        self.initProxy();
        self.computeMovementToUse( astrJointsToExclude = astrJointsToExclude, astrObstacles = astrObstacles );
        nIdxAnimation = 0;
        aMoveOnTheFly = motiontools.transformTimeline( self.movement_arms[nIdxAnimation][0], self.movement_arms[nIdxAnimation][1], self.movement_arms[nIdxAnimation][2], { self.astrHeadPitch[0]: rElevation*0.75, self.astrHeadPitch[1]: rElevation*0.25, self.strHeadYaw: rSide, self.strShoulderRoll: rSide, self.strShoulderPitch: rElevation } );
        self.motion_id_arms = self.motion.post.angleInterpolationBezier( aMoveOnTheFly[0], aMoveOnTheFly[1], aMoveOnTheFly[2] );
        if( bUseHead ):
            self.motion.setAngles( "Head", [rSide,rElevation-0.2], 0.2 );
        self.mutex.unlock();
    # prepare - end
    
    
    def start( self, bUseHead = True, bTrackFace = False, nSayID = -1, astrJointsToExclude = [], astrObstacles = [] ):
        """
        Launch a bodytalk movement.
        - bUseHead
        """
        while( self.mutex.testandset() == False ):
            print( "INF: abcdk.BodyTalk.start: already initing, waiting..." );
            time.sleep( 0.1 );
            
        self.debug( "DBG: abcdk.BodyTalk.start: in..." );        
        self.bUseHead = bUseHead;
        self.bTrackFace = bTrackFace;            
        if( bTrackFace ):
            self.bUseHead = bUseHead; # force the use of the head, to track it's better...
        if( self.bRunning ):
            self.mutex.unlock();
            return;
        self.bRunning = True;
        self.nSayID = nSayID;
        if( self.nSayID != -1 and self.tts == None ):
            self.tts = naoqitools.myGetProxy( "ALTextToSpeech" );
        if( self.nSayID != -1 ): #(so we don't use a say with light)
            if( self.bUseMouth ):
                leds.dcmMethod.setMouthColor( 1., 0xFF );
            else:
                # light leds
                leds.setBrainLedsIntensity( 1., 100, bDontWait = True );
                leds.setEarsLedsIntensity( 1., 100, bDontWait = True );
                rPeriod = 0.1;
                leds.setFavoriteColorEyes( True );
        self.initProxy();
        self.stopCurrentMovements(); # for the case where we are going to rest and want that "going to rest"  now! (add reactivity in dialog)        
        self.computeMovementToUse( astrJointsToExclude = astrJointsToExclude, astrObstacles = astrObstacles );
        self.aLastHeadAngle = self.motion.getAngles( "Head", True ); # store position from launching
        if( self.bTrackFace ):
            #~ if( self.extractor == None ):
                #~ print("INF: abcdk.BodyTalk.start: creating proxy to HaarExtractor..." );
                #~ self.extractor = naoqitools.myGetProxy( "HaarExtractor" );             
            self.rFaceSide = self.aLastHeadAngle[0]; # use position from launching
            self.rFaceElevation = self.aLastHeadAngle[1];
            self.timeLastSeen = time.time()-self.rFaceTrackTimeBeforeLostFace/2; # don't reset head too fast (let's time for detector to find current face)
            try:
                tracking.trackHuman.start2(bTrackFace=True, bEnableRandomMoves=False);
                naoqitools.subscribe( self.strFaceDetectMemoryName, "abcdk.bodytalk.bodyTalk.onFaceDetected" ); # pb: this is not very portable
            except BaseException, err:
                self.mutex.unlock();
                raise( BaseException( "ERR: abcdk.bodytalk.start: tracker init error: %s" % err ) );
        self.mutex.unlock();
    # start - end
    
    def stopCurrentMovements( self ):
        if( self.motion.isRunning( self.motion_id_head ) ):
            try:
                self.motion.stop( self.motion_id_head );
            except BaseException, err:
                self.log( "DBG: should be normal error: %s" % str( err ) );
        if( self.motion.isRunning( self.motion_id_arms ) ):
            try:            
                  self.motion.stop( self.motion_id_arms );
            except BaseException, err:
                self.log( "DBG: should be normal error: %s" % str( err ) );            
        if( self.motion.isRunning( self.motion_id_legs )  and self.bHasRightToUseLegs ):
            try:
                self.motion.stop( self.motion_id_legs );
            except BaseException, err:
                self.log( "DBG: should be normal error: %s" % str( err ) );            
    
    def stop( self, bWaitEndOfRestMovement = True ):
        while( self.mutex.testandset() == False ):
            print( "INF: abcdk.BodyTalk.stop: already initing, waiting..." );
            time.sleep( 0.1 );        
        self.debug( "DBG: abcdk.BodyTalk.stop: in..." );
        if( self.bRunning or self.bPrepared ):                
            if( self.nSayID != -1 ):
                try:
                    self.tts.stop( self.nSayID );
                except BaseException, err:
                    print( "DBG: abcdk.bodytalk.stop: tts err: %s" % str(err) );
            self.bPrepared = False;
            self.bRunning = False;
            nIdxAnimation = 1;
            self.stopCurrentMovements();
            
            aMoveOnTheFly = motiontools.transformTimeline( self.movement_arms[nIdxAnimation][0], self.movement_arms[nIdxAnimation][1], self.movement_arms[nIdxAnimation][2], { self.astrHeadPitch[0]: self.rLastElevation*0.75, self.astrHeadPitch[1]: self.rLastElevation*0.25, self.strHeadYaw: self.rLastSide, self.strShoulderRoll: self.rLastSide*0.2, self.strShoulderPitch: 0. } ); # we don't want to show the direction too much with arms
            self.motion_id_arms = self.motion.post.angleInterpolationBezier( aMoveOnTheFly[0], aMoveOnTheFly[1], aMoveOnTheFly[2] ); # motion_id_arms is used, but it's a whole body movement (but without legs)
            
            if( self.bTrackFace ):
                tracking.trackHuman.stop2();
                try:
                    naoqitools.unsubscribe( self.strFaceDetectMemoryName, "abcdk.bodytalk.bodyTalk.onFaceDetected" );
                except: pass
            if( self.nSayID != -1 ): #(so we don't use a say with light)
                # shut leds
                leds.setBrainLedsIntensity( 0., 100, bDontWait = True );
                leds.setEarsLedsIntensity( 0., 100, bDontWait = True );
                leds.setFavoriteColorEyes( False );
                if( self.bUseMouth ):
                    leds.dcmMethod.setMouthColor( 0.4, 0 );
            
            if( self.eyesMover != None and not self.bTrackFace ):
                self.eyesMover.lookAt3D( [0.,0.], random.random()/2 );
            
            # seems like there's no head movement in the rest motion, so we add it:
            self.rFaceElevation = -0.4;
            aPos =  [self.rFaceElevation*0.65,self.rFaceElevation*0.35,self.rFaceSide];
            aHeadChain = self.astrHeadPitch + [self.strHeadYaw];
            print( "aHeadChain: %s" % aHeadChain );
            print( "aPos: %s" % aPos );
            self.motion_id_head = self.motion.post.angleInterpolation( aHeadChain, aPos, 0.8, True );
            
            if( bWaitEndOfRestMovement ): # You can now choose to not wait here to have a better reactivity
                try: self.motion.wait( self.motion_id_head, -1 );  
                except: pass
                try: self.motion.wait( self.motion_id_arms, -1 );  
                except: pass
                time.sleep( 0.2 );
        self.mutex.unlock();
    # stop - end
    
    def blinkEyes( self ):
        if( not self.bHasEyesLeds ):
            return;
        #~ if(p == "Normal"):
            #~ rColor = 0xffffff
        #~ elif(p == "Happy"):
            #~ rColor = 0x0055ff
        #~ elif(p == "Angry"):
            #~ rColor = 0xff5500
        #~ elif(p == "Redeyes"):
            #~ rColor = 0xff0000    
            
        #nColor = 0xFFFFFF;
        nColor = leds.getFavoriteColorEyes( True );
        if( nColor < 0x7f ):
            nColor = 0xA0A0FF;
        rDuration = 0.05;
        self.leds.post.fadeRGB( "FaceLed0", 0x000000, rDuration );
        self.leds.post.fadeRGB( "FaceLed1", nColor, rDuration );
        self.leds.post.fadeRGB( "FaceLed2", 0x000000, rDuration );
        self.leds.post.fadeRGB( "FaceLed3", 0x000000, rDuration );
        self.leds.post.fadeRGB( "FaceLed4", 0x000000, rDuration );
        self.leds.post.fadeRGB( "FaceLed5", nColor, rDuration );
        self.leds.post.fadeRGB( "FaceLed6", 0x000000, rDuration );
        self.leds.fadeRGB( "FaceLed7", 0x000000, rDuration );

        time.sleep( 0.1 );
        
        rDuration = 0.05;
        self.leds.post.fadeRGB( "FaceLeds", nColor, rDuration );       
    # blinkEyes - end
    
    def update( self, rSide = 0., rElevation = 0. ):
        """
        rSide: side to direct the body talk, nb: it could be overriden if bTrackFace is on and there's a face seen.
        rElevation: elvation "" "" ""
        return False, if we should stop the body tracking
        """
        if( self.bTrackFace ):
            if( False ):
                timeFace, faceInfo = self.mem.getData( self.strFacePositionMemoryName );
                print("faceInfo: " + str( faceInfo ) );
                if( faceInfo != None and len( faceInfo ) > 0 ):
                    face_x, face_y, face_h = faceInfo;
                    rCurrentYaw, rCurrentPitch = self.motion.getAngles( "Head", True ); # current head pos
                    #rCurrentYaw, rCurrentPitch = faceInfo[0][2]; # head pos at photo capture TODO !!!
                    self.rFaceSide = -face_x*0.7 + rCurrentYaw;
                    self.rFaceElevation = face_y*0.4 + rCurrentPitch;
                    self.timeLastSeen = time.time(); # todo: timeFace ?
                if( time.time() - self.timeLastSeen < self.rFaceTrackTimeBeforeLostFace ):
                    rSide = self.rFaceSide;
                    rElevation = self.rFaceElevation;
                else:
                    # dans le doute, on reste sur le dernier angle enregistré (au début, c'est l'angle de lancement du bodytalk)
                    #~ rSide = self.aLastHeadAngle[0];
                    #~ rElevation = self.aLastHeadAngle[1];
                    pass
            if( True ):
                # rely totally on face tracking
                rCurrentYaw, rCurrentPitch = self.motion.getAngles( "Head", True ); # current head pos
                rSide = rCurrentYaw;
                rElevation = rCurrentPitch;
            print("rSide: %f, rElevation: %f" % ( rSide, rElevation ) );
                       
        self.rLastSide = rSide;
        self.rLastElevation = rElevation;
        
        self.debug( "DBG: abcdk.BodyTalk.update: in..." );
        
        if( self.eyesMover != None and not self.bTrackFace ):
            if( random.random() > 0.7 ):
                if( random.random() > 0.5 ):
                    self.eyesMover.lookAt3D( [random.random()*2-1.,random.random()*2-1.], random.random()/2 );
                else:
                    self.eyesMover.lookAt3D( [0.,0.], random.random()/2 );
        
        # we try to have the same behavior even if we call the update very often
        if( time.time() - self.timeLastUpdateTestRandom >= 0.5 ):
            self.timeLastUpdateTestRandom = time.time();
            if( self.bTrackFace ):
                bRelaunchHeadMove = random.random() > 0.85;
            else:
                bRelaunchHeadMove = random.random() > 0.6; # more head move if no tracking
        else:
            bRelaunchHeadMove = False;
            
        if(            self.bUseHead 
            and     ( 
                            ( not self.motion.isRunning( self.motion_id_head ) and bRelaunchHeadMove )
                            or abs(self.aLastHeadAngle[0] - rSide) > 0.1
                            or abs(self.aLastHeadAngle[1] - rElevation) > 0.2
                       ) 
        ):
            self.debug( "DBG: abcdk.BodyTalk.update: launching a new head animation..." );
            try:
                if( self.motion.isRunning( self.motion_id_head ) ):
                    self.motion.stop( self.motion_id_head );
            except BaseException, err:
                self.log( "DBG: should be normal error: %s" % str( err ) );
            nIdxAnimation = numeric.randomDifferent( 0, len(self.movement_head)-1 ); # error: head are beginning from the first animation (not the second one)
            print( "DBG: abcdk.BodyTalk.update: launching head animation: %d" % ( nIdxAnimation - 0 ) );
            #TODO: a gerer directement dans transformTimeLine !!!
            if( not self.bTrackFace ):
                if( self.astrHeadPitch[0] != self.astrHeadPitch[1] ):
                    listModif = { self.astrHeadPitch[0]: rElevation*0.65, self.astrHeadPitch[1]: rElevation*0.35, self.strHeadYaw: rSide };
                else:
                    listModif = { self.astrHeadPitch[0]: rElevation, self.strHeadYaw: rSide };
                aMoveOnTheFly = motiontools.transformTimeline( self.movement_head[nIdxAnimation][0], self.movement_head[nIdxAnimation][1], self.movement_head[nIdxAnimation][2], listModif );
            else:
                aMoveOnTheFly = [  self.movement_head[nIdxAnimation][0], self.movement_head[nIdxAnimation][1], self.movement_head[nIdxAnimation][2]   ];
            self.motion_id_head = self.motion.post.angleInterpolationBezier( aMoveOnTheFly[0], aMoveOnTheFly[1], aMoveOnTheFly[2] );
            self.aLastHeadAngle[0] = rSide;
            self.aLastHeadAngle[1] = rElevation;
            
        if( not self.motion.isRunning( self.motion_id_arms ) ):
            self.debug( "DBG: abcdk.BodyTalk.update: launching a new arms animation..." );
            nIdxAnimation = numeric.randomDifferent( 2, len(self.movement_arms)-1 );
            print( "DBG: abcdk.BodyTalk.update: launching arms animation: %d" % ( nIdxAnimation - 1 ) );
            aMoveOnTheFly = motiontools.transformTimeline( self.movement_arms[nIdxAnimation][0], self.movement_arms[nIdxAnimation][1], self.movement_arms[nIdxAnimation][2], { self.strShoulderRoll: rSide, self.strShoulderPitch: rElevation } );
            self.motion_id_arms = self.motion.post.angleInterpolationBezier( aMoveOnTheFly[0], aMoveOnTheFly[1], aMoveOnTheFly[2] );
            
        if( self.bStanding and not self.motion.isRunning( self.motion_id_legs ) and self.bHasRightToUseLegs ):
            self.debug( "DBG: abcdk.BodyTalk.update: launching a new legs animation..." );
            nIdxAnimation = numeric.randomDifferent( 2, len(self.movement_legs)-1 );
            print( "DBG: abcdk.BodyTalk.update: launching arms animation: %d" % ( nIdxAnimation - 1 ) );
            self.motion_id_legs = self.motion.post.angleInterpolationBezier(self.movement_legs[nIdxAnimation][0], self.movement_legs[nIdxAnimation][1], self.movement_legs[nIdxAnimation][2]);
            
        if( self.bUseHead and random.random() > 0.75 ):
            self.blinkEyes();
            
        if( self.bUseMouth and random.random() > 0.4 ):
            rPeriod = (random.random()/2.)+0.3;
            if( random.random() > 0.9 ):
                nColor = 0;
            else:
                nColor = random.randint(10,0xFF)
            leds.dcmMethod.setMouthColor( rPeriod, nColor );
            
        if( self.nSayID != -1 ):
            bRunning = self.tts.isRunning( self.nSayID );
            if( not bRunning ):
                return False;
        
        return True;
    # update - end
    
    def onFaceDetected( self, strVariableName, newFaceValue ):
        if( newFaceValue != None and len( newFaceValue ) > 0 ):
            print("BodyTalk:onFaceDetected: new face detected: %s" % str(newFaceValue) );
            self.update();
    # onFaceDetected - end
        
    def setDebugMode( self, bNewState = True ):
        """
        Activate (or deactivate) debug mode and printing
        bNewState: True: activate them or False: deactivate them
        """
        self.bDebugMode = bNewState;
    # setDebugMode - end
    
    
    def run( self, strTxt, bUseHead = True, bTrackFace = False, rSide = 0., rElevation = 0., astrJointsToExclude = [], astrObstacles = [], bWaitEndOfRestMovement = True ):
        """
        launch an automatic body talk related to some text
        """
        if( self.tts == None ):
            self.tts = naoqitools.myGetProxy( "ALTextToSpeech" );
          
        self.prepare( bUseHead = bUseHead, rSide = rSide, rElevation = rElevation, bTrackFace = bTrackFace, astrJointsToExclude = astrJointsToExclude, astrObstacles = astrObstacles );
        nSayID = self.tts.post.say( "\\PAU=700\\ " + speech.getTextWithCurrentSpeed( strTxt ) );        
        self.start( bUseHead = bUseHead, bTrackFace = bTrackFace,  nSayID = nSayID, astrJointsToExclude = astrJointsToExclude, astrObstacles = astrObstacles );
        rPeriod = 0.5;
        bMustStop = False;
        while( not bMustStop ):
            bRet = self.update( rSide = rSide, rElevation = rElevation );
            if( not bRet ):
                bMustStop = True;
            time.sleep( rPeriod );
        # end while
        self.stop( bWaitEndOfRestMovement );
    # run - end        
    

# class BodyTalk - end

bodyTalk = BodyTalk();


def autoTest():
    test.activateAutoTestOption();
    bodyTalk.setDebugMode( True );
    bodyTalk.prepare();
    bodyTalk.start();
    for i in range( 10 ):
        bodyTalk.update(); # When running from script, there's a new bug: "Function _isRunning does not exist in module ALMotion"
        time.sleep( 0.5 );
    bodyTalk.stop();
# autoTest - end

if( __name__ == "__main__" ):
    autoTest();
