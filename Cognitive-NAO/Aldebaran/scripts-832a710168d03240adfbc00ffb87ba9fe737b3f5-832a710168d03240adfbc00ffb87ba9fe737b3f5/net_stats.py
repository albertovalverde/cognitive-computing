# -*- coding: utf-8 -*-
#
# Draw all network bandwith consumption every sec / 10 sec
# v0.8
#
# Author: A.Mazel

import time

def getCurrentStat(strInterface = "wlan0" ):
    file = open("/sys/class/net/%s/statistics/tx_bytes" % strInterface )
    buf = file.read()
    file.close()
    nAmount = int(buf)
    return nAmount
    
class NetStats:
    def __init__(self):        
        self.reset()
        
    def reset(self):
        self.anRef = [None,None]
        self.anCurrentSec = [0,0] # for each interface, last sec
        self.aanLast = [[],[]] # for each interface, last 10 sec
        self.anTotal = [0,0]
        self.timeStart = time.time()

    def update(self):
        """
        to be called every 1 sec
        """
        
        print( "%5.0fs " % (time.time() - self.timeStart) ),
                
        nNumInterface = 0
        
        for strInterface in ["eth0", "wlan0"]:
            if self.anRef[nNumInterface] == None:
                self.anRef[nNumInterface] = getCurrentStat( strInterface )                
            amount = getCurrentStat( strInterface )
            self.anCurrentSec[nNumInterface] = amount - self.anRef[nNumInterface]
            if self.anCurrentSec[nNumInterface] < 256:
                self.anCurrentSec[nNumInterface] = 0 # normal ssh stuffs
            self.anRef[nNumInterface] = amount
            
            self.aanLast[nNumInterface].append(self.anCurrentSec[nNumInterface])
            self.aanLast[nNumInterface] = self.aanLast[nNumInterface][-10:]
            nSum = sum(self.aanLast[nNumInterface])
            
            self.anTotal[nNumInterface] += self.anCurrentSec[nNumInterface]
            
            print( "%s: %8.3fk / %8.3fk / %8.3fk -- " % (strInterface,self.anCurrentSec[nNumInterface]/1024.,nSum/1024.,self.anTotal[nNumInterface]/1024.)),
            
            nNumInterface += 1
            
        print("")
            
        
            
        
        
# class NetStats - end


nc = NetStats()

print(  "\nstats: 1 sec / sum 10 sec / from beginning\n" )
while(1):
    nc.update()
    time.sleep(1.)