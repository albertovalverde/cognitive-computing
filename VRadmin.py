# Main

from Config import ConfigAdmin
ConfigAdmin.createConfigFile("Config/Robot Configuration.txt") # Update the configuration .pkl file in case config changes have been made
from VisualRecognition import VRClassifierAdmin
import json

class CallManipulator:
    print "Starting up..."
    admin = VRClassifierAdmin.ClassifierOrganiser()
    admin.collectClassifierInfo()
    print "There are " + str(admin.numberOfClassifiers) + " classifiers present."
    print "This is the current list of classifiers for your credentials:\n" # + json.dumps(manipulator.classifiers, indent=2)
    admin.printClassifiers()

    # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- #
    # START
    print "Main menu:"
    toDo = ''
    while toDo != 'done':
        print "\nWhat do you want to do? Select t, u, d, g, or done. ('t' = train a new classifier, 'u' = update an existing classifier, 'd' = delete, 'g' = get details of a classifier, 'done' = finished)"
        toDo = raw_input()
        funct = admin.functions.get(toDo, admin.wrongLetter)
        funct(admin)

    print "Program will now update the master spreadsheet and .json containing all the classifiers."
    admin.updateMasterSpreadsheet()

    print "Ok, all done!"
