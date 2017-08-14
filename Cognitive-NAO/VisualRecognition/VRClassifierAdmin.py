import simplejson, json, time, pprint, pickle, csv
from os.path import join, dirname
from os import environ
from watson_developer_cloud import VisualRecognitionV3 as VisualRecognition

class ClassifierOrganiser:
    with open('Config/credentials.json') as infile:
        credentials = json.load(infile)
    config = pickle.load(open('Config/configurationDictionary.pkl', 'rb')) # Loads configuration .pkl file into a Python dictionary
    print "Region is", config["regionVr"], "\n"
    version = credentials["region"][config["regionVr"]]["VisualRecognition"]["version"] # Release date of the API version you want to use. Specify dates in YYYY-MM-DD format. REQUIRED.
    api_key = credentials["region"][config["regionVr"]]["VisualRecognition"]["api_key"] # The API key. Required.
    visual_recognition = VisualRecognition(version, api_key=api_key)

    def __init__(self):
        pass

    def printClassifiers(self):
        for j in range(self.numberOfClassifiers):
            print j+1, ':', self.classifierNames[j]
            print ' --> Status:', self.classifiers['classifiers'][j]['status']
            print ' --> ID:', self.classifierIDs[j], "\n"

    def printClasses(self):
        print "\nName:", self.classifierDetails["name"]
        print "Status:", self.classifierDetails["status"]
        print "Date Created:", self.classifierDetails["created"]
        print "Classifier contains the following subclasses:"
        for j in range(len(self.classifierDetails["classes"])):
            print " > " + str(j+1) + ': ' + self.classifierDetails["classes"][j]["class"]

    def collectClassifierInfo(self):
        self.classifiers = self.visual_recognition.list_classifiers()
        # Get number of classifiers currently trained
        try:
            self.numberOfClassifiers = len(self.classifiers["classifiers"])
        except:
            self.numberOfClassifiers = 0
        # Get list of all classifier IDs and classifier names currently trained
        if self.numberOfClassifiers == 0:
            print 'There are no classifiers available.'
            self.classifierNames = None
        else:
            self.classifierIDs = [0] * self.numberOfClassifiers
            self.classifierNames = [0] * self.numberOfClassifiers
            for i in range(self.numberOfClassifiers):
                self.classifierIDs[i] = self.classifiers["classifiers"][i]["classifier_id"]
                self.classifierNames[i] = self.classifiers["classifiers"][i]["name"]

    def selectClassifier(self):
        print "Type in the corresponding number for the classifier and press enter."
        self.printClassifiers()
        n = raw_input()
        try:
            n = int(n) - 1
            if n in range(self.numberOfClassifiers):
                return self.classifierIDs[n]
            else:
                print "Sorry, the number you chose isn't in range."
        except:
            print "Sorry, the number you chose isn't in range."
            return 0

    def getClassifierDetails(self):
        if self.numberOfClassifiers == 0:
            print 'There are no classifiers available.'
        elif self.numberOfClassifiers == 1:
            self.classifierDetails = self.visual_recognition.get_classifier(self.classifiers["classifiers"][0]["classifier_id"])
            self.printClasses()
        else:
            self.classifierID = self.selectClassifier()
            self.classifierDetails = self.visual_recognition.get_classifier(self.classifierID)
            self.printClasses()

    def deleteAClassifier(self):
        self.classifierID = self.selectClassifier()
        if self.classifierID:
            print "Do you really want to delete " + self.classifierID + "? ('y' = delete, press enter to skip)"
            answerD = raw_input()
            if answerD == 'y':
                try:
                    self.visual_recognition.delete_classifier(classifier_id=self.classifierID)
                    print self.classifierID, "has been successfully deleted."
                except:
                    print "Classifier deletion has failed for an unknown reason. Please log on to Bluemix to see what the problem is."
            else:
                print "OK, classifier won't be deleted."

    def createClassifier(self):
        answerT = ""
        classifier_name = "."
        print "This functionality is not yet available.\n"
        while answerT is not 'y' and classifier_name is not '':
            print "Please enter the name for your new classifier and press enter, or just press enter to cancel training:"
            classifier_name = raw_input()
            if classifier_name == '':
                return
            print "Is this correct (y/n)?\n", classifier_name
            answerT = raw_input()
            if answerT == 'y':
                print "New classifier is being trained. This will take some time, please be patient!"
                # positive_sets = ["../Resources/Visual Recognition/Training Sets/1970 VW Beetle.zip", "../Resources/Visual Recognition/Training Sets/Alfa Romeo Brera.zip"]
                # with open(join(dirname(__file__), positive_sets[0]), 'rb') as pos_examples1, \
                #     open(join(dirname(__file__), positive_sets[1]), 'rb') as pos_examples2:
                #
                #     new_classifiers = self.visual_recognition.create_classifier(classifier_name, VW_Beetle_positive_examples=pos_examples1, Alfa_Romeo_positive_examples=pos_examples2)
                #     print json.dumps(new_classifiers, indent=2)
            else:
                pass

    def updateAClassifier(self):
        print "This functionality is not yet available.\n"

    def putjson(self, data, filename):
        jsondata = simplejson.dumps(data, indent = 4, skipkeys = True, sort_keys = True)
        fd = open(filename, 'w')
        fd.write(jsondata)
        fd.close()

    def updateMasterSpreadsheet(self):
        self.collectClassifierInfo()
        self.putjson(self.classifiers, "Resources/Visual Recognition/ListOfVrClassifiers.json")

        with open('Resources/Visual Recognition/ListOfVrClassifiers.csv', 'w') as csvFile:
            csvWriter = csv.writer(csvFile, delimiter = ',', lineterminator = '\n')
            for i in range(self.numberOfClassifiers):
                classifierTemp = [str(self.classifierNames[i]), str(self.classifierIDs[i])]
                csvWriter.writerow(classifierTemp)

        print "NOTE: Be aware that if you have made new classifiers, they may still be in training, and not yet ready to use. Until they have finished training, you will get an error message if you try to use them.\n"

    def wrongLetter(self, placeHolder):
        print 'Letter doesn\'t match possible selection.'

    def done(self):
        pass

    functions = {
    't': createClassifier,
    'u': updateAClassifier,
    'd': deleteAClassifier,
    'g': getClassifierDetails,
    'done': done
    }
