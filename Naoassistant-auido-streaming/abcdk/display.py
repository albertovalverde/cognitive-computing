# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Display tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################


"""Tools to display image on tablet, picoproj..."""


print( "importing abcdk.display" );

import filetools
import naoqitools
import os
import time


class Display():
    """
    For the tablet, we need to have a tmp directory with some web access, so you should do sth like:
        mkdir /tmp/www
        su -c "ln -s /tmp/www /var/www/tmp"

        j'ai ajoute aussi a nginx.conf, avant "location /libs"
        su -c "nano /etc/nginx/nginx.conf"
            location /tmp {
            root /var/www;
        }
        et ne pas oublier de relancer le serveur:
        su -c "/etc/init.d/nginx restart"
    """
    def __init__( self ):
        self.tabletService = None;
        self.strWebLocalPath = "/var/www/tmp/";
        try:
            os.makedirs( "/tmp/www" ); # because /tmp is erased after each restart
        except:
            pass
    # __init__ - end

    def prepare( self ):
        """
        Do the real init, the one that takes time, requires hardware...
        """
        if( self.tabletService == None ):
            self.tabletService = naoqitools.myGetProxy( "ALTabletService" );

            if( self.tabletService == None ):
                print( "WRN: can't connect to ALTabletService: you won't seen image on your tablet..." );            
            else:
                self.strWebRemotePath = "http://%s/tmp/" % self.tabletService.robotIp();
    
    def showImage( self, strPathAndFilename, bDeleteFileJustAfter = False ):
        """
        Return False on error
        """
        self.prepare();
        if( self.tabletService == None ):
            return;
        strHttp = "http://";
        bUrl = False;
        if( strPathAndFilename[:len(strHttp)] != strHttp ):
            # local filename
            strLocalWebTmp = "/tmp/www/";
            bCopiedToTmp = False;
            strFilename = os.path.basename( strPathAndFilename );
            if( strPathAndFilename[:len(strLocalWebTmp)] != strLocalWebTmp ):
                print( "INF: abcdk.display.showImage: copying file to %s" % strLocalWebTmp );                
                bRet = filetools.copyFile( strPathAndFilename, self.strWebLocalPath + strFilename );
                if( not bRet ):
                    return False;
                strRemoteFile = self.strWebRemotePath + strFilename;
                bCopiedToTmp = True;
            else:
                strRemoteFile = self.strWebRemotePath + strPathAndFilename.replace(strLocalWebTmp, "");
        else:
            # url
            strRemoteFile = strPathAndFilename;
            bUrl = True;
        print( "DBG: abcdk.display.show: showing '%s'" % strRemoteFile );

        self.tabletService.preLoadImage( strRemoteFile );
        self.tabletService.showImage( strRemoteFile );
        if( bDeleteFileJustAfter and not bUrl ):
            time.sleep( 0.2 );
            print( "INF: abcdk.display.showImage: unlinking: %s" % strPathAndFilename );
            os.unlink( strPathAndFilename );
            if( bCopiedToTmp ):
                strFileNameToUnlink = self.strWebLocalPath + strFilename;
                print( "INF: abcdk.display.showImage: unlinking-2: %s" % strFileNameToUnlink );
                os.unlink( strFileNameToUnlink );
        return True;
    # showImage - end

    def hide(self):
        self.prepare();
        if( self.tabletService == None ):
            return;
        self.tabletService.hide();
# class Display - end


display = Display();

def autoTest():
    pass

if( __name__ == "__main__" ):
    autoTest();


if( 0 ):
    strPathAndFilename = "http://perso.ovh.net/~mangedisf/mangedisque/images/bologo.gif";
    strHttp = "http://";
    bDiff = ( strPathAndFilename[:len(strHttp)] != strHttp );
    print( ":%s" % strPathAndFilename[:len(strHttp)]  );
    print( "bDiff: %s" % bDiff );