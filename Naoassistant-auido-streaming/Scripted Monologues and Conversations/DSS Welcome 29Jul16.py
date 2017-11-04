from naoqi import ALProxy

# ~--- Obtains the port for Naomi. ---~#
PORT = 9559
# ~--- Obtain the IP address for Naomi. Remember to update the IP.txt file ---~#
text_fileIP = open("../Resources/IP.txt", "r")
currentipdocument = text_fileIP.readlines()
IP = currentipdocument[0]; PORT = 9559
print "Naomi's IP address is " + IP

ttsa = ALProxy("ALAnimatedSpeech", IP, PORT)
autonomousMovement = ALProxy("ALAutonomousMoves", IP, PORT)

autonomousMovement.setBackgroundStrategy("backToNeutral")
ttsa.say("^start(animations/Stand/Gestures/Hey_1)Hello everyone!")
ttsa.say("Welcome to the D S S exploring technologies showcase! I am Naomi, come and have a chat with me and IBM Watson!")
autonomousMovement.setBackgroundStrategy("backToNeutral")
