# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Obstacles tools
# @author The usage team - Living Labs
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Obstacles tools: some method useful to deal with obstacles (mainly when NAO's walking)"""

print( "importing abcdk.obstacles" );

import mutex
import time

import naoqitools
#import nav_mark
import numeric
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG, format=('%(filename)s:%(lineno)d:''%(levelname)s: ' ' %(funcName)s(): '   '%(message)s') )
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

global_aObstacleStates = {'none':0, 'leftSide':1, 'left':2, 'center':3, 'right':4, 'rightSide':5 }
global_bSonarEnabled = False;
def enableSonar( bNewValue ):
    global global_bSonarEnabled;
    print( "INF: abcdk.obstacles.enableSonar: changing from %s to %s" % ( global_bSonarEnabled, bNewValue ) );
    global_bSonarEnabled = bNewValue;

class Manager:
    def __init__( self ):
        self.listBumperEventsName = ["LeftBumperPressed", "RightBumperPressed"];
        self.aLastEvent = []; # a list of pair [time, event value]
        self.mutex = mutex.mutex();
        self.mem = naoqitools.myGetProxy( "ALMemory" );
        self.sonar = naoqitools.myGetProxy( "ALSonar" );
        self.aStrSideName = ["side_left", "left", "center", "right", "side_right"];
        if( self.mem != None ):
            for side in self.aStrSideName:
                self.mem.insertData( "Obstacles/" + side, [time.time()-1000, 0.] );
    # __init__ - end

    def getName( self ):
        return "abcdk.Obstacles";

    def getNameFromIndex( self, nNumEvent ):
        return self.aStrSideName[nNumEvent-1];


    def start( self ):
        self.nNbrHitSonar = 0;
        for event in self.listBumperEventsName:
            naoqitools.subscribe( event, "abcdk.obstacles.manager.onBumper" ); # pb: this is not very portable (todo?)

        global global_bSonarEnabled;
        self.bSonarEnabled = global_bSonarEnabled;
        if( not self.bSonarEnabled ):
            print( "WRN: abcdk.obstacles.Manager.start: sonar are DISABLED" );

        if( self.bSonarEnabled ):
            if( self.sonar != None ):
                self.sonar.subscribe( self.getName(), 0.5, 0. );
        self.bStarted = True;
    # start - end

    def stop( self ):
        for event in self.listBumperEventsName:
            try:
                naoqitools.unsubscribe( event, "abcdk.obstacles.manager.onBumper" );
            except BaseException, err:
                print( "WRN: abck.obstacles.Manager.: Normal error (bStarted=%s), when unsub bumper, and no sub: err: %s" % (self.bStarted,err) );
        try:
            if( self.bSonarEnabled ):
                if( self.sonar != None ):
                    self.sonar.unsubscribe( self.getName() );
        except BaseException, err:
            print( "WRN: abck.obstacles.Manager.: Normal error (bStarted=%s), when unsub sonar, and no sub: err: %s" % (self.bStarted,err) );
        self.bStarted = False;
    # stop - end

    def update( self ):
        """
        return obstacles state:
          0: none
          1: seems to be on the left side (arms)
          2: ... on the left
          3: ... center
          4: ... right
          5: ... right side

        WARNING: obstacles is automatically erased after 2 seconds. (so you need to call update at least every seconds)
        """
        global global_aObstacleStates
        logger.info("Start update")
        while( self.mutex.testandset() == False ):
            print( "%s: INF: abck.obstacles.Manager.update: locked" % time.time() );
            time.sleep( 0.05 );

        # update stuffs
        if( self.bSonarEnabled ):
            sonarValues = self.sonar.getFilteredValues();
            rSonarLimit = 0.30; # was 0.34
            print( "DBG: abck.obstacles.Manager.update.sonarValues: %s" % str(sonarValues) );
            if( sonarValues[0] < rSonarLimit or sonarValues[1] < rSonarLimit ):
                self.nNbrHitSonar += 1;
            else:
                self.nNbrHitSonar = 0;
            if( self.nNbrHitSonar > 2 ):
                print( "INF: Obstacles SONAR triggering" );
                rDiff = sonarValues[0] - sonarValues[1]; # seems to be right, left !!!
                if( abs( rDiff ) < 0.2 ):

                    self.__addEvent(global_aObstacleStates['left']);
                    #nav_mark.navMarkMover.addObstacle( aOffset = [rSonarLimit, 0.1, 0.0] );
                elif( rDiff > 0. ):
                    self.__addEvent(global_aObstacleStates['center']);
                    #nav_mark.navMarkMover.addObstacle( aOffset = [rSonarLimit, 0.0, 0.0] );
                else:
                    self.__addEvent(global_aObstacleStates['right']);
                    #nav_mark.navMarkMover.addObstacle( aOffset = [rSonarLimit, -0.1, 0.0] );

        # eat events
        i = 0;
        logger.info("just before while aLastEvent is %s" % str(self.aLastEvent))
        while( i < len( self.aLastEvent ) ):
            logger.info("in while while")
            if( time.time() - self.aLastEvent[i][0] > 2. ):
                logger.debug("deleting last event %s (timeout)"  % self.aLastEvent[i])
                del self.aLastEvent[i];
            else:
                logger.debug("returning last event %s"  % self.aLastEvent[i])
                ret = self.aLastEvent[i][1];
                self.mutex.unlock();
                return ret;
        self.mutex.unlock();
        return 0;
    # update - end

    def __addEvent( self, nNumEvent ):
        self.mem.raiseMicroEvent( "Obstacles/" + self.getNameFromIndex(nNumEvent), [time.time(), 0.5] );
        self.aLastEvent.append( [ time.time(), nNumEvent ] );
    # __addEvent - end

    def onBumper( self, strVariableName, rVal ):
        print( "%s: INF: abcdk.obstacles.Manager.callback: events name: %s, value: %s" % (time.time(), strVariableName, rVal ) );
        if( rVal < 0.5 ):
            return;
        while( self.mutex.testandset() == False ):
            print( "%s: INF: abcdk.obstacles.Manager.callback: locked" % time.time() );
            time.sleep( 0.05 );
        global global_aObstacleStates
        logger.info("adding event %s" % global_aObstacleStates['center'] )
        self.__addEvent( global_aObstacleStates['center'] );
        self.mutex.unlock();
    # onBumper - end

# class Manager - end

manager = Manager(); # singleton


class Avoider:
    """
    A small avoider du pauvre using current path way to get centered
    """
    def __init__(self):
        self.timeLastBloqued = time.time()-1000;
        self.aTotalOffset = [0,0,0];
        self.nNbrRetryThisObstacle = 0;
        self.prevPosition = [-150,-150,-150];
        self.motion = naoqitools.myGetProxy( "ALMotion" );

    def getMoveDirection(self):
        """
        Return a [move direction (x,y,t), bNewObstacle, bImpossible]
        """
        rTimeSinceLast = time.time() - self.timeLastBloqued;
        print( "INF: abck.obstacles.Avoider.getMoveDirection: rTimeSinceLast: %s" % str( rTimeSinceLast ) );

        bImpossible = False;
        bNewObstacle = False;

        posApprox = self.motion.getRobotPosition( True );
        rDistSinceLast = numeric.dist3D( posApprox, self.prevPosition );
        print( "rDistSinceLast: %s" % str( rDistSinceLast ) );

        # if( time.time() - self.timeLastBloqued > 20. ):
        if( rDistSinceLast > 0.6 ):
            print( "INF: abck.obstacles.Avoider.getMoveDirection: new obstacle!" );
            bNewObstacle = True;
            self.aTotalOffset = [0,0,0];
            self.nNbrRetryThisObstacle = 0;

            arNewDir = [ -0.05, 0.4, 0. ]; # 2013-10-11: Alma Y was 0.28

            #futurePath = nav_mark.navMarkMover.getPath();
            print( "INF: abck.obstacles.Avoider.getMoveDirection: futurePath: %s" % str( futurePath ) );
            if( futurePath != None and len( futurePath ) > 0 ):
                nextPointAngle = futurePath[0][2];
                print( "INF: abck.obstacles.Avoider.getMoveDirection: nextPointAngle: %s" % str( nextPointAngle ) );
                if( np.array_equal( nextPointAngle, [0.]*6 ) ):
                    nextPointAngle = futurePath[1][2]; # first point ? take second


                if( nextPointAngle[1] < 0. ):
                    arNewDir[1] *= -1.;
                if( nextPointAngle[0] < -0.2 ):
                    arNewDir[0] = -0.15;
            self.arPrevDir = arNewDir;

        for i in range( 3 ):
            self.aTotalOffset[i] += self.arPrevDir[i];

        print( "INF: abck.obstacles.Avoider.getMoveDirection: arPrevDir: %s" % self.arPrevDir );
        print( "INF: abck.obstacles.Avoider.getMoveDirection: aTotalOffset: %s" % self.aTotalOffset );
        if( abs( self.aTotalOffset[1] ) > 1.5 or self.nNbrRetryThisObstacle > 5 ):
            bImpossible = True;
            self.aTotalOffset = [0,0,0];

        self.timeLastBloqued = time.time();
        self.nNbrRetryThisObstacle += 1;
        self.prevPosition = self.motion.getRobotPosition( True );
        return [self.arPrevDir, bNewObstacle, bImpossible];
    # getMoveDirection - end

# class Avoider - end

avoider = Avoider();


def autoTest():
    import test
    test.activateAutoTestOption();
    manager.start();
    time.sleep( 1.5 );
    manager.stop();

# autoTest

if __name__ == "__main__":
    autoTest();
