# -*- coding: utf-8 -*-

#
# Sound Acceptance test
# v0.7
#
# Author: A. Mazel & L. George

import sys
import os
import time


def clear_caches():
    if os.name != 'posix':
        return;
    cmd1 = 'sudo sync'
    cmd2 = 'sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"'
    os.popen(cmd1)
    os.popen(cmd2)
    

def test_cpu_int():
    print "test_cpu_int2  : ",
    timeBegin = time.time();
    x = 18
    for i in range( 20 ):
        for i in range(4000):
            x *= 13;
        sys.stdout.write( "#" );
        sys.stdout.flush();
    rDuration = time.time() - timeBegin;
    print("%7.2fs" % rDuration);
    return rDuration;
#test_cpu_int - end

def test_cpu_float():
    print "test_cpu_float2: ",
    timeBegin = time.time();
    x = 18.2
    for i in range( 20 ):
        for i in range(100000):
            x *= 13.5;
        sys.stdout.write( "#" );
        sys.stdout.flush();
    rDuration = time.time() - timeBegin;
    print("%7.2fs" % rDuration);
    return rDuration;
#test_cpu_float - end

def test_disk_write( nMB=200 ):
    print "test_disk_write: ",
    timeBegin = time.time();
    file = open( "temp.tmp", "w" );
    nTimePerLoop = 100000*nMB / 200;
    for i in range( 20 ):
        for i in range(nTimePerLoop):
            file.write( "A"*100 );
        sys.stdout.write( "#" );
        sys.stdout.flush();
    file.flush();
    os.fsync(file.fileno())
    file.close();
    rDuration = time.time() - timeBegin;
    print("%7.2fs (%5.2f Mo/s)" % (rDuration,20*nTimePerLoop*100/(rDuration*1024*1024)));
    return rDuration;
#test_disk_write - end

def test_disk_read( nMB=200 ):
    print "test_disk_read : ",
    clear_caches()
    timeBegin = time.time();
    file = open( "temp.tmp", "r" );
    nTimePerLoop = 100000*nMB / 200;
    for i in range( 20 ):
        for i in range(nTimePerLoop):
            dummy = file.read(1*100);
        sys.stdout.write( "#" );
        sys.stdout.flush();
    file.flush();
    try:
        strMsg = "";
        os.fsync(file.fileno()); 
    except BaseException, err:
        strMsg = "ERR: test_disk_read: while fsyncing: %s" % str(err);
    file.close();
    rDuration = time.time() - timeBegin;
    print("%7.2fs (%5.2f Mo/s)" % (rDuration,20*nTimePerLoop*100/(rDuration*1024*1024)));
    if( strMsg != "" ):
        print strMsg;
    return rDuration;
#test_disk_read - end


def test_perf(nDiskTestSizeMB=200):
    rTotalTime = 0;
    rTotalTime += test_cpu_int();
    rTotalTime += test_cpu_float();
    rTotalTime += test_disk_write(nMB=nDiskTestSizeMB);
    rTotalTime += test_disk_read(nMB=nDiskTestSizeMB);
    os.unlink( "temp.tmp" );
# test_perf - end
    
nDiskTestSizeMB = 200;    
if( len(sys.argv)> 1 ):
    nDiskTestSizeMB=int(sys.argv[1]);
    print( "Changing disk test size to %d MB" % nDiskTestSizeMB );
test_perf(nDiskTestSizeMB=nDiskTestSizeMB);