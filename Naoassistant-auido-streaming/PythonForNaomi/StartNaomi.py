from naoqi import ALProxy

# ~--- Requests user to define whether or not the robot is connected. ---~#
def checkIfRobotIsConnected():
    print "Is the robot connected? (y/n)"
    check = raw_input()
    if check == 'n':
        return False
    else:
        return True

# ~--- Set the IP address for Naomi if it is connected ---~#
def getIP(robotCheck):
    if robotCheck:
        text_fileIP = open("Resources/IP.txt", "r")
        currentipdocument = text_fileIP.readlines()
        IP_ = currentipdocument[0]
        text_fileIP.close()
        print "Type in Naomi's IP address.\nIf this is Naomi's IP address, just hit enter.\n", IP_
        IPDefining = raw_input()
        if IPDefining == '':
            return IP_
        else:
            text_fileIP = open("Resources/IP.txt", "w")
            IP_ = IPDefining
            text_fileIP.write(IP_)
            text_fileIP.close()
            return IP_

def getTextFake():
    print "Insert a message"
    msg = raw_input()
    return msg