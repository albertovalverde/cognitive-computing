# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Navigation tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"""Choregraphe tools"""
print( "importing abcdk.navigation" );

import math
import time

import arraytools
import motiontools
import naoqitools
import numeric

krFovRadianDiagonal = 1.267109036947883;  # 72.6 deg 

def renderMouseEvent( evt, x, y, flags, world ):
    import cv
    if( flags != 0 ):
        print( "renderMouseEvent: %d, %d, 0x%x" % ( x, y, flags ) );
        if( flags & cv.CV_EVENT_RBUTTONDOWN ):
            worldPos = world.renderScale( x, y, True );
            world.gotoPosition( [worldPos[0],worldPos[1],0.], 0. );
# renderMouseEvent - end


class World():
    """
    A world representation that handles amer.
    All measures are in meter
    """
    
    def __init__( self, strNaoAdress = None ):
        self.reset();
        self.strDebugWindowName = False;
        self.strDebugRenderX = 640;
        self.strDebugRenderY = 480;
        self.hfov = math.pi*60.9/180; # total horizontal aperture (sum of each side)
        self.vfov = math.pi*47.6/180;
        if( strNaoAdress != None ):
            self.motion = naoqitools.myGetProxyWithAddr( "ALMotion", strNaoAdress );
        else:
            self.motion = naoqitools.myGetProxy( "ALMotion" );
    # __init__ - end
    
    def reset( self ):
        self.listAmer = {}; # for each amer, its center position, real size and angleZ of its normal
        
        self.viewer = [ [0.,0.,0.], 0., 0. ]; # position, angleZ, bodyAngleZ
        self.aPrevViewer = []; # previous position of viewer (for debug)
        
        self.nearTarget = [[1.,0.,0.],0.];
        self.finalTarget = [[2.,0.,0.],0.];
        
        self.areas = []; # for each area, x top corner, y, then w and h
    # reset - end
    
    def addAmer( self, strID, worldPos, size, rAngleZ = 0. ):
        self.listAmer[strID] = [worldPos, size, rAngleZ];
    # addAmer - end
    
    def updateViewerPosition( self, listAmerSeen ):
        """
        update the approximation position of the viewers based on amer currently seen
        listAmerSeen: a list of [name, distance, angles  ]: with distance: distance of the center of the amer and angles: the angles between the normal and the viewer-object vector (so a perpendicular objest as angles of 0.,0.,0.)
        """
    # updateViewerPosition - end
    
    def updateFromImageVision( self, listInfo ):
        """
        Receive a raw info from ImageVision
        """
        aNameConvert = {
            "Poster1": "Martigny",
            "Poster2": "Jambes",
            "Poster3": "Sparrenburg",
            "Poster4": "Grenoble",
            "Poster5": "Prague",
            "Poster6": "Joconde",
        };
        
        if( listInfo == [] ):
            return;
        
        newPosition = [0.,0.];
        newAngleZ = 0.;
        bUpdated = False;
        # compute seen size of the object
        for obj in listInfo[1]:
            objName = aNameConvert[obj[0][1]];
            rConf = obj[2];
            if( rConf < 0.1 ): # 0.18
                continue;
            listPoint = obj[3];
            x1 = x2 = listPoint[0][0];
            y1 = y2 = listPoint[0][1];
            for point in listPoint[1:]:
                if( x1 > point[0] ):
                    x1 = point[0];
                if( x2 < point[0] ):
                    x2 = point[0];
                if( y1 > point[1] ):
                    y1 = point[1];
                if( y2 < point[1] ):
                    y2 = point[1];                    
            bsx = x2 - x1;
            bsy = y2 - y1;
            
            #~ print( "objName %s: %f, %f" % (objName, bsx, bsy) );
            
            #~ rDistBasedW = ((bsx/2)/math.tan(self.hfov/2)) * self.listAmer[objName][1][0]; # distance based on width of this object
            #~ rDistBasedH = ((bsy/2)/math.tan(self.vfov/2)) * self.listAmer[objName][1][1];
            rDistBasedW = (self.listAmer[objName][1][0]/math.tan(self.hfov/2)) / (bsx) ; # distance based on width of this object
            rDistBasedH = (self.listAmer[objName][1][1]/math.tan(self.vfov/2)) / (bsy) ;
            rAvgDist = (rDistBasedW+rDistBasedH)/2.;
            #~ rAvgDist *= 2; # Add a ratio to make it work better (bug in calculation?)
            rAvgDist /= 2;
            
            #~ rRealSize = bsx * math.cos(rCameraAperture);
            #~ print( "rDistBasedW: %f, rDistBasedH: %f, rAvgDist: %f" %( rDistBasedW, rDistBasedH, rAvgDist ) );
            
            # find orientation
            # sort corner, to have topleft, topright, bottomleft, bottomright
            corner = numeric.findCorner(listPoint);
            #~ print( "corner: %s" % corner );

            
            rTopRoughAngleZ = ( corner[0][1]-corner[1][1] ) / (bsy/2);
            rBottomRoughAngleZ = ( corner[3][1]-corner[2][1] ) / (bsy/2);
            rAvgRoughAngleZ = (rTopRoughAngleZ+rBottomRoughAngleZ)/2;
            #~ rAvgRoughAngleZ = 0.;
            
            #~ print( "rTopRoughAngleZ: %f, rBottomRoughAngleZ: %f, rAvgRoughAngleZ: %f" %( rTopRoughAngleZ, rBottomRoughAngleZ, rAvgRoughAngleZ ) );
            
            #~ print( "obj[2]: %s" %obj[2] );
            newPosition[0] = self.listAmer[objName][0][0]+rAvgDist*math.cos(self.listAmer[objName][2] );
            newPosition[1] = self.listAmer[objName][0][1]+rAvgDist*math.sin(self.listAmer[objName][2] );
            newAngleZ = math.pi - (rAvgRoughAngleZ - self.listAmer[objName][2]);
            # add an offset relative to the position of the object in the camera (bad: it should be using current RoughAngle too !)
            centerObjX = -(x2+x1)/2;
            centerObjY = (y2+y1)/2;
            #~ newPosition[0]  += -centerObjX * math.sin( self.listAmer[objName][2] )*0.4; # 0.4 is relative to the current fov: todo correct it !
            #~ newPosition[1]  += -centerObjX * math.cos( self.listAmer[objName][2] )*0.4; # yes it's well centerObjX !!!
            bUpdated = True;
        
        if( bUpdated ):
            self.aPrevViewer = self.aPrevViewer[:-20];
            self.aPrevViewer.append( arraytools.dup( self.viewer ) );
            rRatioNew = 0.5;
            self.viewer[0][0] = self.viewer[0][0] * (1-rRatioNew) + newPosition[0] * rRatioNew;
            self.viewer[0][1] = self.viewer[0][1] * (1-rRatioNew) + newPosition[1] * rRatioNew;
            self.viewer[1] = self.viewer[1] * (1-rRatioNew) + newAngleZ * rRatioNew;
            newBodyPos = newAngleZ - self.motion.getAngles( "HeadYaw", True )[0];
            self.viewer[2] = self.viewer[2] * (1-rRatioNew) + newBodyPos * rRatioNew;
        
    # updateFromImageVision - end
    
    def getViewerPosition( self ):
        return self.viewer;
    # getViewerPosition - end

    def getViewerBody( self ):
        return self.viewer[2];
    # getViewerPosition - end
    
    def worldToLocal( self, pos ):
        """
        convert a world position to a nao position
        return a nao position [[x,y,z],rAngleZ]
        - pos:  [[x,y,z],rAngleZ] world relative
        """
        #~ dist = [ pos[0][0] - self.viewer[0][0], pos[0][1] - self.viewer[0][1], pos[0][2] - self.viewer[2] ];
        vect = [ pos[0][0] - self.viewer[0][0], pos[0][1] - self.viewer[0][1] ];
        rDist = numeric.norm2D( vect );
        rAbsAngle = math.atan2(vect[1], vect[0] );
        rRelAngle = rAbsAngle - self.viewer[2];
        relPos = [ rDist * math.cos( rRelAngle ), rDist * math.sin( rRelAngle ),0 ];
        rRelAngleZ = pos[1] - self.viewer[2];
        return [relPos, rRelAngleZ];
    # worldToLocal

    def localToWorld( self, pos ):
        """
        convert a nao position to a world position
        return a world position [[x,y,z],rAngleZ]
        - pos:  [[x,y,z],rAngleZ] relative to nao
        """
        rRelAngle = math.atan2( pos[0][1], pos[0][0] );
        rAbsAngle = rRelAngle + self.viewer[2];
        rDist = numeric.norm2D( pos[0] );
        absPos = [ self.viewer[0][0] + rDist * math.cos( rAbsAngle ), self.viewer[0][1] + rDist * math.sin( rAbsAngle ), 0 ];
        rAbsAngleZ = pos[1] + self.viewer[2];
        return [absPos, rAbsAngleZ];
    # localToWorld
    
    def findArea( self, pt ):
        """
        find the area of a specific point.
        return: area [0,n-1] or -1 if not in the area
        pt world a pos[x,y]
        """
        if( len( self.areas ) < 1 ):
            print( "WRN: abcdk.navigation: areas are empty !" );
        for idx, area in enumerate(self.areas):
            if( 
                      pt[0] >= area[0] and pt[0] <= area[0] + area[2]
                and pt[1] >= area[1] and pt[1] <= area[1] + area[3]
            ):
                return idx;
        return -1;
    # findArea - end
    
    # findNearestPoint( 
    
    def findWay( self, orig, final ):
        """
        Find a path from two world points
        Return a list of point or an empty list if not passable
        orig: world point departure [x,y,z]
        final: world point arrival [x,y,z]
        """
        # currently the only error is to jump to the center of the room !
        # area1: first table
        # area2: second table (other part of the L)
        
        # the articulation location of every area connector
        jonctionPoint = [
            [2.4,0.0,0.], # from area 0 to  1
            [2.8,0.4,0.], # from area 1 to  2
        ];
        nOrigArea = self.findArea( orig );
        nFinalArea = self.findArea( final );
        print( "findWay: %s => %s, area: %d => %d" % ( orig, final, nOrigArea, nFinalArea ) );
        if( nOrigArea == -1 or nFinalArea == -1 ):
            return [];
        aPoints = [];
        if( nOrigArea != nFinalArea ):
            # direction
            nDir = nFinalArea - nOrigArea;
            for i in range( nOrigArea, nFinalArea, nDir ):
                aPoints.append( jonctionPoint[i] );
        aPoints.append( final );
        print( "findWay: path: %s" % aPoints );
        return aPoints;
    # findWay - end


    def gotoPosition( self, position, rAngleZ, rAcceptableDistance = 0.2 ):
        """
        launch walk moves to go to a specific destination        
        return True when the robot is at an acceptable distance of the point
        - position: world position
        - rAngleZ: final angle position
        - rAcceptableDistance: rough acceptable distance to be arrived (in meters)
        """
        # walk in direct line (at an average short final point of ~ 50cm)
        finalTarget = [position, rAngleZ];
        relPos = self.worldToLocal( finalTarget );
        rDist = numeric.norm2D( relPos[0] );
        if( rDist <= rAcceptableDistance ):
            print( "abcdk.navigation.gotoPosition( %s ): arrived (dist to point: %5.3f)" % ( position, rDist ) );
            self.motion.stopWalk();
            self.finalTarget = self.nearTarget = finalTarget;
            return True;
            
        listPoint = self.findWay( self.viewer[0], finalTarget[0] );
        if( len( listPoint ) > 0 ):
            nearTarget = [ listPoint[0], finalTarget[1] ]; # here, put angle from there to near TODO
            nearRelTarget = self.worldToLocal( nearTarget );
            #~ self.motion.moveTo( nearRelTarget[0][0], nearRelTarget[0][1], nearTarget[1] );
            #~ self.motion.post.walkTo( nearRelTarget[0][0], nearRelTarget[0][1], nearTarget[1] );
            print( "WALK: launching that command: walk( %5.2f, %5.2f, %5.2f" % ( nearRelTarget[0][0], nearRelTarget[0][1], nearTarget[1] ) );
        else:
            # impassable
            nearTarget = finalTarget = [ [0.,0.,0.], 0.];
            self.motion.stopWalk();
            
        self.nearTarget = nearTarget;
        self.finalTarget = finalTarget;
        
        return False;
    # gotoPosition - end
    
    def gotoAmer( self, strAmerName ):
        """
        positionnate 30cm in front of an amer
        """
        amer = self.listAmer[strAmerName];
        rFront = 0.3;
        frontPosition = [ amer[0][0] + rFront * math.cos(amer[2]), amer[0][1] + rFront * math.sin(amer[2]) ];
        rZ = amer[2] - math.pi;
        self.gotoPosition( frontPosition, rZ );
    # gotoAmer - end
    
    def renderScale( self, x, y, bRevertTransformation = False ):
        """
        scale an x,y in world to the map coordinate on screen
        return xscreen and yscreen
        bRevertTransformation: do the reverse operation: screen to world
        """
        rMaxX = 4.0;
        rMaxY = 2.4;
        rScaleX = self.strDebugRenderX / rMaxX;
        rScaleY = self.strDebugRenderY / rMaxY;
        if( bRevertTransformation ):
            return ( (560-x)/rScaleX, (y-100)/rScaleY );
        return ( int(0.5+560-(x*rScaleX)),int(0.5+100+y*rScaleY) );
    # renderScaleWorldToDraw - end
        
        
    def renderSimulation( self, nPauseMillisec = 1 ):
        """
        render in a windows current state
        return False when the window want to close
        """
        import cv
        if( self.strDebugWindowName == False ):
            # windows creation
            self.strDebugWindowName = "abcdk.navigation";
            cv.NamedWindow( self.strDebugWindowName, cv.CV_WINDOW_AUTOSIZE );
            cv.SetMouseCallback( self.strDebugWindowName, renderMouseEvent, self );
        bufferImageToDraw = cv.CreateImage( (self.strDebugRenderX, self.strDebugRenderY), cv.IPL_DEPTH_8U, 3 );
        cv.Set( bufferImageToDraw, (255,255,255) );
        if( 1 ):
            # draw the 'L Shape'        
            tableColor = (120,120,120);
            cv.Line( bufferImageToDraw, self.renderScale( -0., -0.4 ), self.renderScale( 3.2, -0.4 ), tableColor );
            cv.Line( bufferImageToDraw, self.renderScale( 3.2, -0.4 ), self.renderScale( 3.2, 1.6 ), tableColor );
            cv.Line( bufferImageToDraw, self.renderScale( 3.2, 1.6 ), self.renderScale( 2.4, 1.6 ), tableColor );
            cv.Line( bufferImageToDraw, self.renderScale( 2.4, 1.6 ), self.renderScale( 2.4, 0.4 ), tableColor );
            cv.Line( bufferImageToDraw, self.renderScale( 2.4, 0.4 ), self.renderScale( 0.0, 0.4 ), tableColor );
            cv.Line( bufferImageToDraw, self.renderScale( 0.0, 0.4 ), self.renderScale( 0.0, -0.4 ), tableColor );
        
        # draw the amer
        amerColor = (200,0,0);
        for k,amer in self.listAmer.iteritems():
            #~ print( "amer[2]: %s" %amer[2] );
            rCoefX = math.sin( amer[2] );
            rCoefY = math.cos( amer[2] );
            cv.Line( bufferImageToDraw, self.renderScale( amer[0][0]+rCoefX*amer[1][0]/2, amer[0][1]+rCoefY*amer[1][1]/2 ), self.renderScale( amer[0][0]-rCoefX*amer[1][0]/2, amer[0][1]-rCoefY*amer[1][1]/2 ), amerColor, thickness=2 );

        # draw viewer trail:
        for pos in self.aPrevViewer:
            trailColor = (100,0,100);
            cv.Circle( bufferImageToDraw, self.renderScale( pos[0][0], pos[0][1] ), 3, trailColor );
            rLenOrientation = 0.2;
            #~ cv.Line( bufferImageToDraw, self.renderScale( pos[0][0], pos[0][1] ), self.renderScale( pos[0][0] + rLenOrientation * math.cos(pos[1] ), pos[0][1] + rLenOrientation * math.sin(pos[1] ) ), trailColor );
            rLenFov = 0.5/2;
            cv.Line( bufferImageToDraw, self.renderScale(  pos[0][0],  pos[0][1] ), self.renderScale(  pos[0][0] + rLenFov * math.cos(  pos[1] - self.hfov/2),  pos[0][1] + rLenFov * math.sin(  pos[1] - self.hfov/2) ), trailColor );
            cv.Line( bufferImageToDraw, self.renderScale(  pos[0][0],  pos[0][1] ), self.renderScale(  pos[0][0] + rLenFov * math.cos(  pos[1] + self.hfov/2),  pos[0][1] + rLenFov * math.sin(  pos[1] + self.hfov/2) ), trailColor );
            

        # draw the viewer
        viewerColor = (200,0,200);
        cv.Circle( bufferImageToDraw, self.renderScale( self.viewer[0][0], self.viewer[0][1] ), 3, viewerColor );
        #~ rLenOrientation = 0.2;
        #~ cv.Line( bufferImageToDraw, self.renderScale( self.viewer[0][0], self.viewer[0][1] ), self.renderScale( self.viewer[0][0] + rLenOrientation * math.cos(self.viewer[1] ), self.viewer[0][1] + rLenOrientation * math.sin(self.viewer[1] ) ), viewerColor );
        # draw cone showing fov
        fovColor = (100,0,100);
        rLenFov = 0.5;
        cv.Line( bufferImageToDraw, self.renderScale( self.viewer[0][0], self.viewer[0][1] ), self.renderScale( self.viewer[0][0] + rLenFov * math.cos( self.viewer[1] - self.hfov/2), self.viewer[0][1] + rLenFov * math.sin( self.viewer[1] - self.hfov/2) ), fovColor );
        cv.Line( bufferImageToDraw, self.renderScale( self.viewer[0][0], self.viewer[0][1] ), self.renderScale( self.viewer[0][0] + rLenFov * math.cos( self.viewer[1] + self.hfov/2), self.viewer[0][1] + rLenFov * math.sin( self.viewer[1] + self.hfov/2) ), fovColor );
        
        # draw the body orientation
        rLenOrientation = 0.2;
        cv.Line( bufferImageToDraw, self.renderScale( self.viewer[0][0], self.viewer[0][1] ), self.renderScale( self.viewer[0][0] + rLenOrientation * math.cos(self.viewer[2] ), self.viewer[0][1] + rLenOrientation * math.sin(self.viewer[2] ) ), viewerColor );
        
        # draw target
        
        rCrossSize = 0.1;
        targetColor = (180,180,180);
        cv.Line( bufferImageToDraw, self.renderScale( self.nearTarget[0][0], self.nearTarget[0][1] ), self.renderScale( self.nearTarget[0][0] + rCrossSize * math.cos(self.nearTarget[1] ), self.nearTarget[0][1] + rCrossSize * math.sin(self.nearTarget[1] ) ), targetColor );
        cv.Line( bufferImageToDraw, self.renderScale( self.nearTarget[0][0] - (rCrossSize/2) * math.sin(self.nearTarget[1] ), self.nearTarget[0][1] + (rCrossSize/2) * math.cos(self.nearTarget[1] ) ), self.renderScale( self.nearTarget[0][0] + (rCrossSize/2) * math.sin(self.nearTarget[1] ), self.nearTarget[0][1] - (rCrossSize/2) * math.cos(self.nearTarget[1] ) ), targetColor );
        targetColor = (0,0,0);
        cv.Line( bufferImageToDraw, self.renderScale( self.finalTarget[0][0], self.finalTarget[0][1] ), self.renderScale( self.finalTarget[0][0] + rCrossSize * math.cos(self.finalTarget[1] ), self.finalTarget[0][1] + rCrossSize * math.sin(self.finalTarget[1] ) ), targetColor );
        cv.Line( bufferImageToDraw, self.renderScale( self.finalTarget[0][0] + rCrossSize/2 * math.sin(self.finalTarget[1] ), self.finalTarget[0][1] + rCrossSize/2 * math.cos(self.finalTarget[1] ) ), self.renderScale( self.finalTarget[0][0] - rCrossSize/2 * math.sin(self.finalTarget[1] ), self.finalTarget[0][1] - rCrossSize/2 * math.cos(self.finalTarget[1] ) ), targetColor );
        
        if( 0 ):
            # debug localToWorld
            relpos = [[0.3, 0., 0.],math.pi/4];
            pos = self.localToWorld( relpos );
            relpos2 = self.worldToLocal( pos );
            print( "conv local -> world -> local:\n%s,\n%s,\n%s\n" % ( relpos, pos, relpos2 ) );
            cv.Circle( bufferImageToDraw, self.renderScale( pos[0][0], pos[0][1] ), 3, trailColor );
            rLenOrientation = 0.3;
            cv.Line( bufferImageToDraw, self.renderScale( pos[0][0], pos[0][1] ), self.renderScale( pos[0][0] + rLenOrientation * math.cos(pos[1] ), pos[0][1] + rLenOrientation * math.sin(pos[1] ) ), trailColor );
        
        
        # render
        cv.ShowImage( self.strDebugWindowName, bufferImageToDraw );
        nKey =  cv.WaitKey(nPauseMillisec);
        bContinue = not ( nKey == ord( 'q' ) or nKey == ord( 'Q' ) );
        return bContinue;
    # renderSimulation - end
    
# World - end

def constructWorld_HumavipsAltair(strNaoAdress):
    # use appu_demos/humavips/humavips_altair.vrd
    world = World(strNaoAdress);
    world.addAmer( "Martigny",      [0.61,-0.4,0.56], [0.4,0.56], math.pi/2 );
    world.addAmer( "Jambes",         [1.5,-0.4,0.58], [0.545,0.41], math.pi/2 );
    world.addAmer( "Sparrenburg", [2.61,-0.4,0.54], [0.39,0.57], math.pi/2 );
    world.addAmer( "Grenoble",      [3.20,0.18,0.6], [0.63,0.28], math.pi );
    world.addAmer( "Prague",         [3.20,1.02,0.46], [0.4,0.5], math.pi );
    world.addAmer( "Joconde",        [-0.23,0.4,0.56], [0.375,0.57], 0. );
    
    world.areas = [
            [0., -0.4, 2.4, 0.8], # for each area, x top corner, y, then w and h
            [2.4, -0.4, 0.8, 0.8],
            [2.4, 0.4, 0.8, 1.6],
        ];    
    return world;
# constructWorld_HumavipsAltair - end

def autoTest_World():
    strNaoAdress = "10.0.253.151";
    world = constructWorld_HumavipsAltair(strNaoAdress);
    # seen1 is the results analyse from: martigny_seen1.png (the object is really at 0.55cm)
    seen1 =  [
                   [1363018562, 345017], 
                   [
                      [
                        ['Front', 'Poster1'], 
                        32, 
                        0.46478873491287231, 
                        [
                          [0.51458388566970825, -0.74386024475097656], 
                          [-0.079677492380142212, -0.5916283130645752], 
                          [-0.0829973965883255, 0.20412908494472504],   
                          [0.64073991775512695, 0.22834776341915131]
                        ]
                      ]
                   ]
                 ];
    world.updateFromImageVision( seen1 );
    seen2 = [[1363111076, 962845], [[['Front', 'Poster1'], 13, 0.18309858441352844, [[0.46146553754806519, -0.56740963459014893], [-0.0829973965883255, -0.7922976016998291], [-0.23571263253688812, 0.32868239283561707], [0.56770223379135132, 0.35290113091468811]]]]];
    world.updateFromImageVision( seen2 );
    seen3 = [[1363113022, 703082], [[['Front', 'Poster1'], 36, 0.50704222917556763, [[0.30211055278778076, -0.37365999817848206], [-0.19587385654449463, -0.38057965040206909], [-0.32534977793693542, 0.39441892504692078], [0.36186864972114563, 0.47053489089012146]]]]]
    world.updateFromImageVision( seen3 );
    seen4 = [[1363113889, 327015], [[['Front', 'Poster5'], 7, 0.029520295560359955, [[0.0829973965883255, 0.37711980938911438], [-0.063078008592128754, 0.36328056454658508], [-0.043158624321222305, 0.16607110202312469], [0.086317308247089386, 0.17299072444438934]]]]]    
    world.updateFromImageVision( seen4 );
    world.renderSimulation(001);
    #~ return
    
    mem = naoqitools.myGetProxyWithAddr( "ALMemory", strNaoAdress );
    bContinue = True;
    rDT = 0.;
    while( bContinue ):
        seen = mem.getData( "PictureDetected" );
        #~ print( "seen: %s" % seen );
        world.updateFromImageVision( seen );
        bContinue = world.renderSimulation(500);
        
        #~ world.viewer = [ [3., 0., 0. ], 0., 0. ]; # hard test
        #~ world.gotoPosition( [3.,1.02,0.], 0. );
        #~ world.gotoAmer( "Sparrenburg" );
        #~ world.gotoAmer( "Prague" );
        #~ world.gotoAmer( "Joconde" );
        rDT += 0.1;
    
    # auto loop !
    
# autoTest_World - end

class MoveToObject:
    """
    A coarse and quick approach using vision toward a dedicated object
    """
    def __init__( self ):
        self.averageW = 0.5; # to filter a bit (begin by an average size)
        self.averageH = 0.5;
        self.timeLastSend = time.time() - 100;
        self.motion = naoqitools.myGetProxy( "ALMotion" );
        self.bStopped = False;
        
        
    def update( self, objectPos, rRealDiagonalSize, rDistToReach = 0.2, bFilterPosition = False ):
        """
        update move to last seen position of object
        objectPos: position of the target [x,y,w,h] (in camera space [-0.5,0.5], w and h in [0,1])
        rRealDiagonalSize: real size of the diagonal of the object (in m)
        rDistSizeToReach: average distance to achieve (in m)
        bFilterInput: when detected object is subject to error (eg VisionInfo, it's important to filter it)
        return -1, 0, 1: too near, good, too far
        
        The analyse is intended to be of about 1fps at worst
        """
        print( "INF: abcdk.navigation.MoveToObject.update: received position: %s, real diago size: %5.3f, dist to reach:%5.3f" % (str(objectPos), rRealDiagonalSize,  rDistToReach ) );
        if( self.bStopped ):
            print( "WRN: abcdk.navigation.MoveToObject.update: it has been stopped => do nothing..." );
            return;
        rRatioNew = 0.3;
        if( bFilterPosition ):
            self.averageW = self.averageW * (1.-rRatioNew) + objectPos[2]*rRatioNew;
            self.averageH = self.averageH * (1.-rRatioNew) + objectPos[3]*rRatioNew;        
            objectPos[2] = self.averageW;        
            objectPos[3] = self.averageH;        
        print( "INF: abcdk.navigation.MoveToObject.update: after filtering: position: %s" % str( objectPos ) );        
        rDirHead = self.motion.getAngles( "HeadYaw", True )[0];
        rDir = objectPos[0]+ rDirHead;
        #~ rDistToWalk = rTargetSizeToReach - objectPos[2];
        rSeenSize = numeric.norm2D( [objectPos[2], objectPos[3]] );
        rCurrentDist = (rRealDiagonalSize * (1.41 / 2.0) / (math.tan(krFovRadianDiagonal / 2.0)))  / rSeenSize;
        print( "INF: abcdk.navigation.MoveToObject.update: rSeenSize: %5.3f, rCurrentDist: %5.2f" % ( rSeenSize,rCurrentDist ) );
        rDistToWalk = rCurrentDist - rDistToReach;
        print( "INF: abcdk.navigation.MoveToObject.update: objectPos: %s, rDistToWalk: %f rDir: %f" % (str( objectPos ), rDistToWalk, rDir/2 ) );
        rMargin = 0.05;
        retValue = -2;
        if( rDistToWalk > rMargin ):            
            retValue = 1;
        elif( rDistToWalk < -rMargin ):
            retValue = -1;
        else:
            retValue = 0;
        # track object with headALMotion.post.angleInterpolation( "HeadYaw", 0., 2., True );
        #~ if( self.moveID != -1 ):
            #~ try:
                #~ self.motion.stop( self.moveID );
            #~ except BaseException, err:
                #~ self.log( "INF: error: %s" % str( err ) );
        if( 1 ):
            # track using pitch
            self.motion.changeAngles( "HeadPitch", objectPos[1]*0.4, 0.2 );
            
        if( time.time() - self.timeLastSend < 1.5 ):
            if( 1 ):
                # track only if not walking  (because walking is intended to go in the right direction)
                self.motion.changeAngles( "HeadYaw", objectPos[0]*0.4, 0.2 );
            
            return retValue; # can't send too much move command        
        self.timeLastSend = time.time();        
        self.motion.setAngles( "HeadYaw", 0., 0.2 ); # slowly put head to body axis
        rDistToWalk *= 0.5; # our small amortissement (eg: because while walking the time to compute give us an error, so to prevent going thru the object...)
        self.motion.stopMove();
        self.motion.moveTo( rDistToWalk*math.cos(rDir), rDistToWalk*math.sin(rDir), rDir );
        print( "INF: abcdk.navigation.MoveToObject.update: return %d" % retValue );
        return( retValue );
        
    def stop(self):
        print( "INF: abcdk.navigation.MoveToObject: stopping..." );
        self.motion.stopMove();
        self.bStopped = True;
        
# class MoveToObject - end

class PreciseMoveToObject:
    """
    A fine and precise positionning to an object
    """
    def __init__( self ):
        self.motion = naoqitools.myGetProxy( "ALMotion" );
        self.bInUpdate = False;        
        self.reset();
        
    def reset( self ):
        self.averageW = 0.; # to filter a bit
        self.averageH = 0.;
        self.timeLastWalkSend = time.time() - 100;
        self.nCptLost = 0;
        self.rPrevDist = -1;
        self.rDistBetweenObjectAvg = 0.;  # a filtered value
        self.bStopped = False;
        self.currentBodyMove = [0.5]*3;
        self.bForceNextUpdateToWalk = False;
        
    def update( self, objectSeen, rDistBetweenObjectToAchieve, rAverageX = 0., bUseWholeBody = True ):
        """
        precise position
        - objectSeen: a list of object seen in the camera (in camera space [-0.5,0.5]) could be [] if not seen that time
        - rDistBetweenObjectToAchieve: dist between object to maximize (in full camera space [0,1])
        - rAverageX: average X to achieve (in camera space [-0.5,0.5])
        - bUseWholeBody: you could made fine move using hip movement
        return 0: not achieved, 1: timeout, 2: timeout but try anyway, 3: good positionnate
        """
        print( "INF: abcdk.navigation.PreciseMoveToObject.update: received objectSeen: %s, rDistBetweenObjectToAchieveToAchieve: %5.3f, rAverageX: %5.3f" % (str(objectSeen), rDistBetweenObjectToAchieve, rAverageX ) );
        if( self.bStopped ):
            print( "WRN: abcdk.navigation.PreciseMoveToObject.update: it has been stopped => do nothing..." );
            return 0;
            
        if( self.bInUpdate ):
            print( "WRN: abcdk.navigation.PreciseMoveToObject.update: already in => do nothing..." );
            return 0;
        self.bInUpdate = True;
        retVal = 0;
        x1,y1 = objectSeen[0];
        x2,y2 = objectSeen[1];
        if( x1 == -1. or x2 == -1 ):
            self.nCptLost += 1;
            if( self.nCptLost > 5 ):
                if( abs(self.rPrevDist - rDistBetweenObjectToAchieve) < 0.05 ):
                    retVal = 2;
                else:
                    retVal = 1;
                return retVal;
            self.bInUpdate = False;
            return 0;
        dx = x2-x1;
        dy = y2-y1;    
        rDistBetweenObjectCurrent = math.sqrt( dx*dx+dy*dy );
        self.rPrevDist = rDistBetweenObjectCurrent;
        self.rDistBetweenObjectAvg = self.rDistBetweenObjectAvg * 0.5 + rDistBetweenObjectCurrent * 0.5;
        # we invert it to be in the same orientation than a classic image (positif to the right and positif to the bottom)
        
        # compute position of median point
        rAvgX = (x2+x1)/2.;
        rAvgY = (y2+y1)/2.;
        #~ rDistYToCenter = (rAvgY - (nSizeY/2))/float(nSizeY);
        rDistYToCenter = rAvgY * 0.2; # a small amortissement
        print( "INF: abcdk.navigation.PreciseMoveToObject.update: moving headpitch to %f" % rDistYToCenter );
        if( self.motion != None ): # for autotest
            self.motion.post.changeAngles( "HeadPitch", rDistYToCenter, 0.1 );
            # don't track on yaw as it has to be in the same direction than the body !!!
        print( "INF: abcdk.navigation.PreciseMoveToObject.update: rDistBetweenObjectCurrent: %f, rAvgX: %5.2f, rAvgY: %5.2f" % (rDistBetweenObjectCurrent,rAvgX, rAvgY) ); # 47 pixels => 12cm; 25 pix => 23cm; 85px => 4cm
        # rOptimalDistance > rDistBetweenObjectCurrent => too far
        bDistanceOk = (rDistBetweenObjectToAchieve > rDistBetweenObjectCurrent and rDistBetweenObjectToAchieve - rDistBetweenObjectCurrent < 0.003)  or ( rDistBetweenObjectCurrent > rDistBetweenObjectToAchieve and rDistBetweenObjectCurrent - rDistBetweenObjectToAchieve < 0.025 ); # a bit far (was 2)  or a bit near (was 6)
        if( bDistanceOk and abs( rAverageX - rAvgX ) < 0.05 ): # side was < 5
            self.bInUpdate = False;
            return 3;
        if( time.time() - self.timeLastWalkSend < 0.8 or self.motion.moveIsActive() ):
            # wait a bit that motion.walk is inited, stuffs, don't load it too much...
            self.bInUpdate = False;
            return 0;
        rDisplaceX = 0;
        rDisplaceY = 0;
        if( not bDistanceOk ):
            rModifier = abs(rDistBetweenObjectToAchieve - rDistBetweenObjectCurrent )*10; # a modifier giving an idea of the distance between current and goal [0..1..2]
            print( "INF: abcdk.navigation.PreciseMoveToObject.update: dist rModifier: %f" % rModifier );
            if( rModifier > 2):
                rModifier = 2;
            rStep = 0.04*rModifier;
            print( "INF: abcdk.navigation.PreciseMoveToObject.update: rStep: %f" % rStep );
            if( rDistBetweenObjectToAchieve > rDistBetweenObjectCurrent ):
                # pas assez de pixel: on est trop loin
                rAddY = 0.;
                rAddY = ( rAverageX - rAvgX ) / 6; # add a bit of angle, so that, we won't pass a coté de l'objet too much
                print( "INF: abcdk.navigation.PreciseMoveToObject.update: rAddY: %f" % rAddY );
                if( rDistBetweenObjectToAchieve > self.rDistBetweenObjectAvg +15 ):
                    # the filtered value is very far from the optimal: let's walk MORE !
                    print( "INF: abcdk.navigation.PreciseMoveToObject.update: WALK MORE !!!" );
                    rStep *= 2; # was *3
                if( self.motion != None ):
                    rDisplaceX = +rStep;
                    rDisplaceY = +rAddY;
            else:
                if( self.motion != None ):
                    rDisplaceX = -rStep;
        else:
            rModifier = abs(rAverageX - rAvgX ) * 2;
            print( "INF: abcdk.navigation.PreciseMoveToObject.update: X rModifier: %f" % rModifier );
            if( rModifier > 2 ):
                rModifier = 2;
            rStep = 0.04*rModifier;
            if( rAverageX > rAvgX ):
                # move to left
                rDisplaceY = +rStep;
            else:
                rDisplaceY = -rStep;
        if( rDisplaceX != 0. or rDisplaceY != 0 ):
            #~ bUseWholeBody = False;
            rCoefBodyMove = 5;
            if( bUseWholeBody and not self.bForceNextUpdateToWalk ):
                bTooFar = not numeric.inRange01( self.currentBodyMove[0]+rCoefBodyMove*rDisplaceX ) or not numeric.inRange01( self.currentBodyMove[1]+rCoefBodyMove*rDisplaceY );                
                if( bTooFar ):
                    print( "WRN: abcdk.navigation.PreciseMoveToObject.update: too far, walking" );
                    self.bForceNextUpdateToWalk = True;
                    self.currentBodyMove = [0.5]*3;
                else:
                    self.currentBodyMove[0] += rDisplaceX*rCoefBodyMove;
                    self.currentBodyMove[1] += rDisplaceY*rCoefBodyMove;
                print( "moveTorso: %s" % ( self.currentBodyMove ) );
                motiontools.moveTorso( self.currentBodyMove[0], self.currentBodyMove[1] ); # move is blocking
            else:
                self.bForceNextUpdateToWalk = False;
                self.motion.moveTo( rDisplaceX, rDisplaceY, 0. );
                self.timeLastWalkSend = time.time();
        self.bInUpdate = False;
        return 0;
    # update - end
        
    def stop(self):
        print( "INF: abcdk.navigation.PreciseMoveToObject: stopping..." );
        self.motion.stopMove();
        self.bStopped = True;
        
# class PreciseMoveToObject - end

def autoTest_PreciseMoveToObject():
    navigate = PreciseMoveToObject();    
    # a bit to the left, quite center
    seen = [[-0.18652038276195526, 0.01046025101095438], [-0.19905956089496613, 0.24058577418327332]];
    navigate.update(seen, 0.3);
    navigate.update(seen, 0.3);
# autoTest_PreciseMoveToObject() - end


def autoTest():
    import test
    test.activateAutoTestOption();    
    #~ autoTest_World();
    pass
# autoTest - end
    
        

if( __name__ == "__main__" ):
    #~ autoTest(); 
    autoTest_PreciseMoveToObject();
    pass

if( False ):
    # real example at 50cm of a datamatrix
    rRealDiagonalSize = numeric.norm2D( [0.09,0.09] );
    print( "rRealDiagonalSize: %f" % rRealDiagonalSize );
    rSeenSize = numeric.norm2D( [0.175,0.179] );
    rSeenSize = 0.24;
    print( "rSeenSize: %f" % rSeenSize );
    rDist = (rRealDiagonalSize * (1.41 / 2.0) / (math.tan(krFovRadianDiagonal / 2.0)))  / rSeenSize;
    print( "rDist: %f" % rDist );
