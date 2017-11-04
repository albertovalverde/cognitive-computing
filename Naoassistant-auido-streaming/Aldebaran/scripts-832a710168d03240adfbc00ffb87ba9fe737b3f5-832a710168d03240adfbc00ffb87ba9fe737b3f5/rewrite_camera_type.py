# -*- coding: utf-8 -*-
#
# Rewrite Head ID. 
# This script is for internal use only and should never used by customers!
#
# v0.7
#
# syntaxe: scriptname ROBOT_IP NEW_HEAD_ID
# You need to enter the IP of your NAO in the configuration section.
#
# Author: A.Mazel

import naoqi
import sys
import time

def rewriteCameraType( strRobotIP, cameraType):
    print( "\nINF: Setting a New camera type: " + str(cameraType))
    dcm = naoqi.ALProxy( "DCM", strRobotIP, 9559 )
    dcm.preferences( "Add", "Head", "RobotConfig/Head/Device/Camera/Version", str(cameraType) ) # to set the type to nao new stereo head
    
    time.sleep(2)
    # Save the pref in the head
    dcm.preferences( "Save", "Head", "", 0.0 )
    
    print( "" )
    print( "INF: now you should restart hal and naoqi. Enter the password 'root'" )
    print( "INF: eg, a command like that:" )
    print( 'nao stop ; su -c "/etc/init.d/hald restart"' )
# rewriteHeadID - end


if __name__ == '__main__':    
    if len(sys.argv) < 3:
        print( "Rewrite a camera type.\n" )
        print( "WARNING: Internal use only!" )
        print( "WARNING: Will mess the store and kpi and ..." )
        print("")
        print( "Syntaxe: %s <robot_ip> <camera_type>" % sys.argv[0] )
        exit(0)
    
    rewriteCameraType( sys.argv[1], sys.argv[2])
    
