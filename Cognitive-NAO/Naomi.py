################################################################################
# Author: Andreas Maude                                                        #
# Last update: Aug 29, 2016                                                    #
# Version: 3.00                                                                #
## ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ##

import time, random, csv, simplejson, json, pickle, os, datetime, watchdog, threading
from sys import platform as _platform
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from naoqi import ALProxy
from NLC import NLC, NLCClassifierAdmin
from Config import ConfigAdmin
from PersonalityInsights import A1_PersonalityInsights
from VisualRecognition import WatsonVisualRecognition
from PythonForNaomi import RobotFunctions, StartNaomi
from Naked.toolshed.shell import execute_js, muterun_js

#~--- Initial startup stuff ---~#
robotCheck = StartNaomi.checkIfRobotIsConnected() # Check if robot is connected
PORT = 9559 # Get Naomi's port
IP_global = StartNaomi.getIP(robotCheck) # Get Naomi's IP address
ConfigAdmin.createConfigFile("Config/Robot Configuration.txt") # Update the configuration .pkl file in case config changes have been made
config = pickle.load(open('Config/configurationDictionary.pkl', 'rb')) # Loads configuration .pkl file into a Python dictionary
credentials = json.load(open('Config/credentials.json')) # Loads all Bluemix credentials
# NLCClassifierAdmin.ClassifierOrganiser().updateMasterSpreadsheet() # Make sure that all NLC classifier IDs are up to date
# print "File containing NLC classifier information successfully updated.\n"
## ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ##

#~--- Define the Watson demos ---~#
watsonVisRec = WatsonVisualRecognition.VisRecHandler(credentials["region"][config["regionVr"]]["VisualRecognition"], config)
HandleNlc = NLC.ResponseHandler(credentials["region"][config["regionNlc"]]["NLC"], config) # This handles the determination of response for each NLC classification.

def PersonalityInsights():
    personSunburst = PersonalityInsightsSession.PI_Request()

def DoVisualRecognition():
    picture = watsonVisRec.identifyPicture("/Resources/Visual Recognition/" + config["pictureFileName"])
    response_phrase = "This could be a " + picture["top_classification"] + ". I am " + str(picture["top_confidence"]) + "% sure."
    print "Returned possibilities are:"
    if len(picture["all_classifications"]):
        for i in range(min(len(picture["all_classifications"]), config["vrNumToReturn"])):
            print " -> " + str(i+1) + ": " + picture["all_classifications"][i]["type_hierarchy"] + "/" + picture["all_classifications"][i]["class"] + ", " + str(picture["all_classifications"][i]["score"]*100) + "%"
    else:
        print "None. This could be an error."
    return [response_phrase, picture["time_elapsed"]]

def DoTextRecognition():
    picture = watsonVisRec.recogniseText("/Resources/Visual Recognition/" + config["pictureFileName"])
    text = ', '.join(picture["text"])
    response_phrase = "The text in the picture is:\n" + text
    if text == '':
        response_phrase = "I can't read any text in this picture!"
    return [response_phrase, picture["time_elapsed"]]

def DoFacialRecognition():
    picture = watsonVisRec.recogniseFaces("/Resources/Visual Recognition/" + config["pictureFileName"])

    if picture["identity_recognised"]:
        response_phrase = 'This looks like ' + picture["identity"] + ". I am " + str(picture["identity_confidence"]) + "% sure."
    elif picture["person_recognised"]:
        response_phrase = 'This looks like a ' + picture["gender"] + ", who is between the ages of " + str(picture["age_min"]) + " and " + str(picture["age_max"])
    else:
        response_phrase = "I can't recognise a person in this picture!"
    return [response_phrase, picture["time_elapsed"]]

def DoCustomVisualRecognition():
    picture = watsonVisRec.identifyCustomClassifier("/Resources/Visual Recognition/" + config["pictureFileName"])
    response_phrase = "I think this is a " + picture["top_classification"] + ". I am " + str(picture["top_confidence"]) + "% sure."
    return [response_phrase, picture["time_elapsed"]]

def DoNothing():
    return [0, 0]

watsonFunctions = { # dictionary of the Watson demos that Naomi can perform
'DoNothing': DoNothing,
'DoTextRecognition': DoTextRecognition,
'DoVisualRecognition': DoVisualRecognition,
'DoFacialRecognition': DoFacialRecognition,
'DoCarRecognition': DoCustomVisualRecognition,
'PersonalityInsights': PersonalityInsights
}

## ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ##

def getext(filename): # Get the file extension from a file.
    return os.path.splitext(filename)[-1].lower()

def confirmReadyForStartUp():
    print "\nReady to get started!"

### ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ###
class MyHandler(FileSystemEventHandler):
    def __init__(self, observer, config):
        self.ListOfNlcClassifiers = json.load(open('Resources/NLC/ListOfNlcClassifiersManual.json', 'r')) # load JSON with list of nlc classifiers
        self.nlcClassifierName = config["firstNlc"] # The first NLC classifier to analyse text against
        self.nlcClassifierID = self.ListOfNlcClassifiers[self.nlcClassifierName] # The first NLC classifier ID to analyse text against
        self.Naomi = RobotFunctions.Robot(IP_global, PORT, config, robotCheck) # Initialise all robot functions in variable "Naomi"
        self.Naomi.StartUp() # Get Naomi out of rest mode, stand it up, set eye colour, etc.
        self.observer = observer # Set variable to control the watchdog observer that is looking at the transcript file directory for change events

        confirmReadyForStartUp() # Print start-up message to let user know that everything has been started smoothly

    def on_deleted(self, event):
        pass # Ignore file deletions from the transcripts folder

    def on_modified(self, event):
	
	import speech_recognition as sr
	
	import speech_recognition as sr
	r = sr.Recognizer()
	with sr.WavFile("speech.wav") as source:              # use "test.wav" as the audio source
		audio = r.record(source)   
			 
		# Speech recognition using Google Speech Recognition
		try:
				# for testing purposes, we're just using the default API key
				# to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
				# instead of `r.recognize_google(audio)`
			print("You said: " + r.recognize_google(audio))
		except sr.UnknownValueError:
			print("Google Speech Recognition could not understand audio")
		except sr.RequestError as e:
			print("Could not request results from Google Speech Recognition service; {0}".format(e))
	 

        if _platform == "darwin": # Make code Mac compatible
            files_in_dir = [event.src_path + "/" + f for f in os.listdir(event.src_path)]
            mod_file_path = max(files_in_dir, key=os.path.getmtime)
            transcript = mod_file_path
            transcript2 = r.recognize_google(audio)
        else:
            transcript2 = r.recognize_google(audio)
            transcript = event.src_path






        #if getext(transcript) == '.txt': # When a .txt file is received, register that a new sentence has been returned from Speech to Text

            self.observer.unschedule_all() # Stop listening to events temporarily while the current transcript is being processed.
            self.Naomi.startThinking() # Prepare to wait for the Watson NLC response
            #nlcClassification = HandleNlc.classifyText(transcript, self.nlcClassifierName,self.nlcClassifierID)  # Retrieve NLC
            nlcClassification = HandleNlc.classifyText(transcript2, self.nlcClassifierName, self.nlcClassifierID)  # Retrieve NLC

            nlcResponse = HandleNlc.returnResponse(self.nlcClassifierName, nlcClassification) # Retrieve correct response for the NLC classification

            self.Naomi.printAndSay (nlcResponse[0]) # Print and say (if the robot is connected) the verbal response
            self.nlcClassifierID = nlcResponse[1] # Set the classifier ID to be used for the next NLC request
            self.nlcClassifierName = nlcResponse[2] # Set the classifier name to be used for the next NLC request
            self.Naomi.RobotFunctionDec(nlcClassification) # If user requested a robot function, execute that function

            watsonResponse = watsonFunctions.get(nlcClassification, DoNothing)() # If user requested a Watson function, execute that function
            if watsonResponse[0]:
                self.Naomi.printAndSay(watsonResponse[0])
                print "Time required for API call:", watsonResponse[1], "seconds"

            self.Naomi.previousUtterance = nlcResponse[0] # Hold the last thing Naomi said in a variable so that it can be repeated if required

            os.remove(transcript) # Remove the transcript file as it is no longer needed
        time.sleep(1) # Wait some time before listening to events again to ensure no clutter
        self.observer.schedule(event_handler, path='./Resources/Transcript Text Files', recursive=False) # Start listening to events again

### ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ## ~--~ ###

# Watchdog .txt event handling
if __name__ == "__main__":
    observer = Observer()
    event_handler = MyHandler(observer, config)
    observer.schedule(event_handler, path='./Resources/Transcript Text Files', recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
