# Main

from Config import ConfigAdmin
ConfigAdmin.createConfigFile("Config/Robot Configuration.txt") # Update the configuration .pkl file in case config changes have been made
from NLC import NLCClassifierAdmin
import json

class CallManipulator:
    print "Starting up..."
    manipulator = NLCClassifierAdmin.ClassifierOrganiser()
    manipulator.getListsOfClassifiers()
    print "There are " + str(manipulator.numberOfClassifiers) + " classifiers present."
    print "This is the current list of classifiers for your credentials:\n" # + json.dumps(manipulator.classifiers, indent=2)
    for j in range(manipulator.numberOfClassifiers):
        print j+1, ':', manipulator.classifierNames[j], '--> created at', manipulator.classifiers['classifiers'][j]['created']

    # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- #
    # START
    print "\nMain menu:\nWelcome to NLC manipulation tool, where you can update your NLC classifiers."
    toDo = ''
    while toDo != 'done':
        print "\nWhat do you want to do? Select t, r, d, c, or done. ('t' = train a new classifier, 'r' = retrain an old classifier, 'd' = delete, 'c' = check status, 'done' = finished)"
        toDo = raw_input()
        funct = manipulator.functions.get(toDo, manipulator.wrongLetter)
        funct(manipulator)

    print "Program will now update the master spreadsheet and .json containing all the classifiers."
    manipulator.updateMasterSpreadsheet()

    print "Ok, all done!"
