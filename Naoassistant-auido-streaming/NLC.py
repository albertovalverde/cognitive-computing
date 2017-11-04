import os, csv, pprint, ast, json, random
from watson_developer_cloud import NaturalLanguageClassifierV1
# The response handler class loads up .csv files with intent-response mappings. You input an NLC classification (an intent) to the class and it returns the verbal response associated with that intent.

class ResponseHandler():
    def __init__(self, credentials, config):
        self.responseDictionary = {}
        self.minThreshold = config["nlcConfThreshold"]
        self.numToReturn = config["nlcNumToReturn"]
        # self.responseDictionary is set up to contain the verbal responses to all the possible NLC classifications. It is in dictionary format, making it very quick and easy to access responses once an NLC classification has been returned.

        for fileName in os.listdir('Resources/NLC/Responses'):
            if fileName.endswith(".csv"):
                classifierName = os.path.splitext(fileName)[0][1:]
                self.responseDictionary[classifierName] = [{}]
                reader = csv.reader(open('Resources/NLC/Responses/' + fileName, 'rb'))
                for row in list(reader):
                    self.responseDictionary[classifierName][0][row[0]] = row[1:]

        self.unsurePhrase = ["Sorry, I didn't understand you.", "Could you please repeat that?", "I missed what you said, sorry!", "Excuse me, I didn\'t catch that!", "Sorry, I misheard you!", "Please say that again."]

        self.classifiersList = json.load(open('Resources/NLC/ListOfNlcClassifiersManual.json', 'rb'))
        self.ListnlcJSON = json.load(open('Resources/NLC/ListOfNlcClassifiers.json', 'r')) # load the JSON with the list of nlc classifiers
        print "The available NLC classifiers are:"
        for i in range(len(self.ListnlcJSON["classifiers"])):
            print self.ListnlcJSON["classifiers"][i]["name"]

        self.natural_language_classifier = NaturalLanguageClassifierV1(
          username=credentials["username"],
          password=credentials["password"]
          )

        self.printClassCreationSuccess()

    def printClassCreationSuccess(self):
        print "\nReturn language response class successfully initialised.\n"

    def returnResponse(self, classifierName, classification):
        if classification == "Unsure":
            verbalResponse = random.choice(self.unsurePhrase)
            nextClassifier = classifierName
        else:
            verbalResponse = self.responseDictionary[classifierName][0][classification][1]
            nextClassifier = self.responseDictionary[classifierName][0][classification][0]
        return [verbalResponse, self.classifiersList[nextClassifier], nextClassifier] # 1. verbal response, 2. next classifier id, 3. next classifier, 4. bool indicating robot function

    def classifyText(self, transcriptionTxtFileName, classifierName, classifierID):
        print "\nCurrently using the " + classifierName + " classifier." # Print which NLC classifier is currently being used.

        textToClassify = transcriptionTxtFileName
        print "User: " + textToClassify
        try:
            classes = self.natural_language_classifier.classify(classifierID, textToClassify) # return the classification
            classification = classes["top_class"] # get the top class
            confidence = classes["classes"][0]["confidence"] # get the confidence score

            print ">> Classification: " + classification + ", " + '%.2f' % (confidence*100) + '%'

            for i in range(1, min(self.numToReturn, 10)):
                print " >> Alternative " + str(i) + ": " + classes["classes"][i]["class_name"] + ", " + '%.2f' % (classes["classes"][i]["confidence"]*100) + '%'

            if confidence < self.minThreshold: # apply the confidence threshold
                return "Unsure"
            else:
                return classification
        except:
            print "NLC classification failed. Please check that all NLC classifiers are ready for use and not still in their training phase. Hit ctrl + c and restart the program."

    def extractTextFromFile(self, txtFileName):
        return open(txtFileName, "r").readlines()[0] # Read sentence to be classified from .txt file
