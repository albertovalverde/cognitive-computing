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
# #
autonomousMovement = ALProxy("ALAutonomousMoves", IP, PORT)

# a list of class objects to mimic a C type array of structures
# tested with Python24       vegaseat       30sep2005
class Spot(object):
    """__init__() functions as the class constructor"""

    def __init__(self, title=None, media=None):
        self.title = title
        self.media = media

# make a list of class Person(s)
personList = []
personList.append(Spot("ESSILOR LAUNCHES NEW PROGRESSIVE LENS. VARILUX X SERIES.", "A1.jpg",))
personList.append(Spot("Essilor introduces a new vision frontier arms length vision with its new premium progressive lens Varilux X series.", "A2.jpg"))
personList.append(Spot("Essilor has developed a new type of lens, which it says is the first progressive lens to match the maximum volume of vision that wearers need in the modern world.", "A3.jpg",))



# create proxy on ALMemory for comunicate with webview
memProxy = ALProxy("ALMemory", IP, PORT)
# raise event. Data can be int, float, list, string


#print personList[2].title




# autonomousMovement.setBackgroundStrategy("backToNeutral")
# ttsa.say("^start(animations/Stand/Gestures/Hey_1)Hello everyone!")
# ttsa.say("Welcome to the ESSILOR exploring technologies showcase! I am ESSI, come and have a chat with me and Artificial Inteligence Services!")
# autonomousMovement.setBackgroundStrategy("backToNeutral")
#
#welcomePhrases = [("Welcome to the ESSILOR exploring technologies showcase! I am Essi!, come and have a chat with Artificial Inteligence Services!",1),"Hi everyone, welcome to the Essilor innovation labs show case!", "Hi and welcome to the DEMO of Essilor vision therapy for children","Hi and welcome to Essilor cognitive computing workshop!", "Hello! Have a great time at the Essilor innovation labs show case!"]
#print welcomePhrases
i = 0
while i <= 900:
    #ttsa.say(random.choice(welcomePhrases))
    rdm = random.choice(personList)




    print rdm.title
    memProxy.raiseEvent("RobotSay", str(rdm.title))

    print rdm.media

    memProxy.raiseEvent("RobotSpot", str(rdm.media))
    ttsa.say(rdm.title)
    #print random.choice(welcomePhrases)

    time.sleep(10)
