from naoqi import ALProxy

# ~--- Obtains the port for Naomi. ---~#
PORT = 9559
# ~--- Obtain the IP address for Naomi. Remember to update the IP.txt file ---~#
text_fileIP = open("../Resources/IP.txt", "r")
currentipdocument = text_fileIP.readlines()
IP_ = currentipdocument[0]; PORT = 9559
print "Naomi's IP address is " + IP_

ttsa = ALProxy("ALAnimatedSpeech", IP_, PORT)
autonomousMovement = ALProxy("ALAutonomousMoves", IP_, PORT)

autonomousMovement.setBackgroundStrategy("backToNeutral")
ttsa.say("Hi Jason, I hope you're having a good day")
raw_input()
ttsa.say("")
raw_input()
ttsa.say("")

autonomousMovement.setBackgroundStrategy("backToNeutral")
