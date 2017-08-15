import json, sys, pickle, time
import speech_recognition as sr
from PythonForNaomi import RobotFunctions, StartNaomi
from NLC import NLC, NLCClassifierAdmin
from VisualRecognition import WatsonVisualRecognition
config = pickle.load(
    open('Config/configurationDictionary.pkl', 'rb'))  # Loads configuration .pkl file into a Python dictionary
credentials = json.load(open('Config/credentials.json'))  # Loads all Bluemix credentials
# NLCClassifierAdmin.ClassifierOrganiser().updateMasterSpreadsheet() # Make sure that all NLC classifier IDs are up to date
# print "File containing NLC classifier information successfully updated.\n"
## ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ~--~ ##
# ~--- Define the Watson demos ---~#
watsonVisRec = WatsonVisualRecognition.VisRecHandler(credentials["region"][config["regionVr"]]["VisualRecognition"],
                                                     config)
HandleNlc = NLC.ResponseHandler(credentials["region"][config["regionNlc"]]["NLC"],
                                config)  # This handles the determination of response for each NLC classification.
def confirmReadyForStartUp():
    print "\nReady to get started!"
def PersonalityInsights():
    personSunburst = PersonalityInsights.PI_Request()
def DoVisualRecognition():
    picture = watsonVisRec.identifyPicture("/Resources/Visual Recognition/" + config["pictureFileName"])
    response_phrase = "This could be a " + picture["top_classification"] + ". I am " + str(
        picture["top_confidence"]) + "% sure."
    print "Returned possibilities are:"
    if len(picture["all_classifications"]):
        for i in range(min(len(picture["all_classifications"]), config["vrNumToReturn"])):
            try:
                print " -> " + str(i + 1) + ": " + picture["all_classifications"][i]["type_hierarchy"] + "/" + \
                      picture["all_classifications"][i]["class"] + ", " + str(picture["all_classifications"][i]["score"] * 100) + "%"
            except:
                print picture
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
        response_phrase = 'This looks like ' + picture["identity"] + ". I am " + str(
            picture["identity_confidence"]) + "% sure."
    elif picture["person_recognised"]:
        response_phrase = 'This looks like a ' + picture["gender"] + ", who is between the ages of " + str(
            picture["age_min"]) + " and " + str(picture["age_max"])
    else:
        response_phrase = "I can't recognise a person in this picture!"
    return [response_phrase, picture["time_elapsed"]]
def DoCustomVisualRecognition():
    picture = watsonVisRec.identifyCustomClassifier("/Resources/Visual Recognition/" + config["pictureFileName"])
    response_phrase = "I think this is a " + picture["top_classification"] + ". I am " + str(
        picture["top_confidence"]) + "% sure."
    return [response_phrase, picture["time_elapsed"]]
def DoPlayGame():
     print "into DoPlayGame of Cognitive_services"
    # response_phrase = "Into playGame congnitive services"
    # time.sleep(100)
    # return [response_phrase, 0]
def DoNothing():
    return [0, 0]
watsonFunctions = {  # dictionary of the Watson demos that Naomi can perform
        'DoNothing': DoNothing,
        'DoTextRecognition': DoTextRecognition,
        'DoVisualRecognition': DoVisualRecognition,
        'DoFacialRecognition': DoFacialRecognition,
        'DoCarRecognition': DoCustomVisualRecognition,
        'PersonalityInsights': PersonalityInsights,
        'PlayGame': DoPlayGame
}
class CognitiveService():
    def __init__(self, IP_global, PORT, robotCheck):
        #threading.Thread.__init__(self)

        self.ListOfNlcClassifiers = json.load(
            open('Resources/NLC/ListOfNlcClassifiersManual.json', 'r'))  # load JSON with list of nlc classifiers
        self.nlcClassifierName = config["firstNlc"]  # The first NLC classifier to analyse text against
        self.nlcClassifierID = self.ListOfNlcClassifiers[
            self.nlcClassifierName]  # The first NLC classifier ID to analyse text against
        self.Naomi = RobotFunctions.Robot(IP_global, PORT, config,
                                          robotCheck)  # Initialise all robot functions in variable "Naomi"
        self.Naomi.StartUp()  # Get Naomi out of rest mode, stand it up, set eye colour, etc.
        #self.speechToPath = speech_path

        self.google = sr.Recognizer() # google specch recognition
        self.roboCheck = robotCheck
        self.HandleNlc= HandleNlc

        confirmReadyForStartUp()  # Print start-up message to let user know that everything has been started smoothly
    def on_deleted(self, event):
        pass  # Ignore file deletions from the transcripts folder
    def on_modified(self,filename):

        print filename


        with sr.WavFile(filename) as source:  # use "test.wav" as the audio source
            audio = self.google.record(source)

            # Speech recognition using Google Speech Recognition
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`

                if self.roboCheck:
                    transcript = self.google.recognize_google(audio)
                else:
                    transcript = StartNaomi.getTextFake()
                print "User Say: " + transcript

                if transcript == 'stop':
                    sys.exit('Stop - Error!')



                #self.Naomi.startThinking()  # Prepare to wait for the Watson NLC response

                nlcClassification = self.HandleNlc.classifyText(transcript, self.nlcClassifierName, self.nlcClassifierID)  # Retrieve NLC

                #print nlcClassification + "___" + self.nlcClassifierName
                nlcResponse = self.HandleNlc.returnResponse(self.nlcClassifierName,
                                                       nlcClassification)  # Retrieve correct response for the NLC classification
                print nlcResponse

                self.Naomi.printAndSay(nlcResponse[0])  # Print and say (if the robot is connected) the verbal response
                self.nlcClassifierID = nlcResponse[1]  # Set the classifier ID to be used for the next NLC request
                self.nlcClassifierName = nlcResponse[2]  # Set the classifier name to be used for the next NLC request
                self.Naomi.RobotFunctionDec(nlcClassification)  # If user requested a robot function, execute that function

                watsonResponse = watsonFunctions.get(nlcClassification,
                                                     DoNothing)()  # If user requested a Watson function, execute that function
                if watsonResponse[0]:
                    self.Naomi.printAndSay(watsonResponse[0])
                    print "Time required for API call:", watsonResponse[1], "seconds"

                self.Naomi.previousUtterance = nlcResponse[
                    0]  # Hold the last thing Naomi said in a variable so that it can be repeated if required

            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                #Start()
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

            #Start()
    def on_CheckPlay(self, filename, value):
        print filename
        with sr.WavFile(filename) as source:  # use "test.wav" as the audio source
            audio = self.google.record(source)
            # Speech recognition using Google Speech Recognition
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                if self.roboCheck:
                    transcript = self.google.recognize_google(audio)
                else:
                    transcript = StartNaomi.getTextFake()
                print "User Say: " + transcript # Print and say (if the robot is connected) the verbal response
                self.Naomi.printAndSay(
                    "You say: " + transcript)

                print "Compare:" + str(value) + " = " + str(transcript)
                if str(value) == str(transcript):
                    self.Naomi.printAndSay("WOU! You are a champion!, congratulations!")  # Print and say (if the robot is connected) the verbal response
                else:
                    self.Naomi.printAndSay(
                        "Ohhhh! Sorry! you must to improve your vision becouse the correct number is: " + str(value))  # Print and say (if the robot is connected) the verbal response

                return True
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                return False
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
                return False
    def on_SayAndPrint(self,message):
        self.Naomi.printAndSay(message)
