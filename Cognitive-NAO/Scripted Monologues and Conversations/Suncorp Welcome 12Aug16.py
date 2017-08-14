from naoqi import ALProxy
import time
import random

# ~--- Set the IP address for Naomi if it is connected ---~#
def getIP():
    text_fileIP = open("../Resources/IP.txt", "r")
    currentipdocument = text_fileIP.readlines()
    IP_ = currentipdocument[0]
    text_fileIP.close()
    print "Type in Naomi's IP address.\nIf this is Naomi's IP address, just hit enter.\n", IP_
    IPDefining = raw_input()
    if IPDefining == '':
        return IP_
    else:
        text_fileIP = open("../Resources/IP.txt", "w")
        IP_ = IPDefining
        text_fileIP.write(IP_)
        text_fileIP.close()
        return IP

PORT = 9559
IP = getIP() # Get Naomi's IP address

ttsa = ALProxy("ALAnimatedSpeech", IP, PORT) # Animated speech proxy

welcomePhrases = ["Hi everyone, welcome to the suncorp innovation labs show case!", "Hi and welcome to suncorp!", "Hello! Have a great time at the suncorp innovation labs show case!"]

i = 0
while i <= 900:
    ttsa.say(random.choice(welcomePhrases))
    time.sleep(6)
