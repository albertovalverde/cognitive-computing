# Code by Andreas Maude, 31/05/2016
# Last update: 22/06/2016

from watson_developer_cloud import NaturalLanguageClassifierV1
import simplejson, json, csv, os, pickle

class ClassifierOrganiser:
    with open('Config/credentials.json') as infile:
        credentials = json.load(infile)
    config = pickle.load(open('Config/configurationDictionary.pkl', 'rb')) # Loads configuration .pkl file into a Python dictionary

    natural_language_classifier = NaturalLanguageClassifierV1(
    username=credentials["region"][config["regionNlc"]]["NLC"]["username"],
    password=credentials["region"][config["regionNlc"]]["NLC"]["password"]
    )

    def __init__(self):
        # Get list of all training files in the training folder
        self.trainingFiles = []
        for filename in os.listdir("Resources/NLC/Training"):
            self.trainingFiles.append(filename)

    def getListsOfClassifiers(self):
        # Get .json dictionary of all currently trained classifiers
        self.classifiers = self.natural_language_classifier.list()
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

    def done(self):
        pass

    def delete_classifier(self):
        answerD = ''
        while answerD != "n" and answerD != "no":
            print "Which of these classifiers do you want to delete? (select number in the list and hit enter, or hit enter to return to the main menu)"
            for i in range(self.numberOfClassifiers):
                print str(i + 1) + ") " + self.classifierNames[i] + ': ' + self.classifierIDs[i]
            listnumber = raw_input()
            if listnumber == '':
                return
            try:
                listnumber = int(listnumber) - 1
            except:
                return

            if listnumber in range(self.numberOfClassifiers):
                print "Do you want to delete this one? (y = delete)\n" + self.classifierNames[listnumber]
                answerD = raw_input()
                if answerD == 'y':
                    classes = self.natural_language_classifier.remove(self.classifierIDs[listnumber])
                    print "Classifier has been deleted."
                    self.getListsOfClassifiers()
                else:
                    print "Ok, it won't be deleted."
            else:
                print "Sorry, the number you chose isn't in the range."

    def train_a_new_classifier(self):
        answerT = ''
        while answerT != "n" and answerT != "no":
            print "Select the name of the training file by typing in the corresponding number and pressing enter. Remember, your .csv training file must be sitting in the 'Resources/NLC/Training' folder. Hit enter to skip."
            for filename in self.trainingFiles:
                print str(self.trainingFiles.index(filename) + 1) + ". " + str(filename)
            listnumber = raw_input()
            if listnumber == '':
                return
            try:
                listnumber = int(listnumber) - 1
            except:
                print 'Invalid number.'
                return
            trainingFile = self.trainingFiles[listnumber]
            print "You've selected " + trainingFile
            classifierName = trainingFile[:-4]
            if self.doesNotExist(classifierName):
                print "Initiating training..."
                with open('Resources/NLC/Training/' + trainingFile, 'rb') as training_data:
                  classifier = self.natural_language_classifier.create(
                    training_data=training_data,
                    name=classifierName,
                    language='en'
                  )
                print "Done!"
                print(json.dumps(classifier, indent=2))
                self.getListsOfClassifiers()
            else:
                pass

            print "Do you want to train another classifier? (y/n)"
            answerT = raw_input()

    def doesNotExist(self, name):
        if self.classifierNames is not None and name in self.classifierNames:
            print "There is already a classifier present for this name (" + name + "). In order to avoid confusion, the program will not train another classifier with the same name. Either rename the training file, or select 'retrain' from the main menu."
            return 0
        else:
            return 1

    def retrain_a_classifier(self):
        answerR = ''
        while answerR != "n":
            print "Which classifier do you want to retrain? Remember, you must have a .csv training file sitting in the 'Resources/NLC/Training' folder. Hit enter to skip."
            for i in range(self.numberOfClassifiers):
                print str(i + 1) + ") " + self.classifierNames[i] + ': ' + self.classifierIDs[i]
            listnumber = raw_input()
            if listnumber == '':
                return
            try:
                listnumber = int(listnumber) - 1
            except:
                print "Invalid number."
                return
            if listnumber in range(self.numberOfClassifiers):
                classifierName = self.classifierNames[listnumber]
                trainingFile = classifierName + '.csv'
                # Check to make sure that there is a training file for this classifier
                if trainingFile in self.trainingFiles:
                    print "Do you want to retrain " + classifierName + '?'
                    answerR2 = raw_input()
                    if answerR2 == 'y':
                        print "Deleting classifier..."
                        classes = self.natural_language_classifier.remove(self.classifierIDs[listnumber])
                        print "Training new classifier..."
                        with open('Resources/NLC/Training/' + trainingFile, 'rb') as training_data:
                          classifier = self.natural_language_classifier.create(
                            training_data=training_data,
                            name=classifierName,
                            language='en'
                          )
                        print(json.dumps(classifier, indent=2))
                        self.getListsOfClassifiers()
                    else:
                        print "Ok, it won't be retrained."
                        return
                else:
                    print 'Training file does not exist for this classifier.'
                    return
            else:
                print "Sorry, the number you chose isn't in the range."
                return

            print "Do you want to retrain another classifier? (y/n)"
            answerR = raw_input()

    def get_status_of_classifier(self):
        print "Which classifier do you want the status of? (select number in list)"
        for i in range(self.numberOfClassifiers):
            print str(i + 1) + ") " + self.classifierNames[i] + ': ' + self.classifierIDs[i]
        listnumber = raw_input()
        listnumber = int(listnumber) - 1

        if listnumber in range(self.numberOfClassifiers):
            status = self.natural_language_classifier.status(self.classifierIDs[listnumber])
            #print (json.dumps(status, indent=2))
            print "'" + self.classifierNames[listnumber] + "' " + "Status: " + status["status"] + '. ' + status["status_description"]
        else:
            print "Sorry, the number you chose isn't in the range."

    def putjson(self, data, filename):
        jsondata = simplejson.dumps(data, indent = 4, skipkeys = True, sort_keys = True)
        fd = open(filename, 'w')
        fd.write(jsondata)
        fd.close()

    def wrongLetter(self, placeHolder):
        print 'Letter doesn\'t match possible selection.'

    def updateMasterSpreadsheet(self):
        self.classifiers = self.natural_language_classifier.list()
        self.putjson(self.classifiers, "Resources/NLC/ListOfNlcClassifiers.json")
        numberOfClassifiers = len(self.classifiers["classifiers"])

        with open('Resources/NLC/ListOfNlcClassifiers.csv', 'w') as csvFile:
            csvWriter = csv.writer(csvFile, delimiter = ',', lineterminator = '\n')
            for i in range(numberOfClassifiers):
                classifierTemp = [str(self.classifiers["classifiers"][i]["name"]), str(self.classifiers["classifiers"][i]["classifier_id"])]
                csvWriter.writerow(classifierTemp)

            jsondumpfile = "{"
            endcomma = '\",'
            for i in range(numberOfClassifiers):
                if i == numberOfClassifiers - 1:
                    endcomma = '\"\n}'
                jsondumpfile += "\n\t\"" + str(self.classifiers["classifiers"][i]["name"]) + "\": \"" + str(self.classifiers["classifiers"][i]["classifier_id"]) + endcomma

            obj = open('Resources/NLC/ListOfNlcClassifiersManual.json', 'wb')
            obj.write(jsondumpfile)
            obj.close
        print "NOTE: Be aware that if you have made new classifiers, they may still be in training, and not yet ready to use. Until they have finished training, you will get an error message if you try to use them.\n"

    functions = {
    't': train_a_new_classifier,
    'r': retrain_a_classifier,
    'd': delete_classifier,
    'c': get_status_of_classifier,
    'done': done
    }
