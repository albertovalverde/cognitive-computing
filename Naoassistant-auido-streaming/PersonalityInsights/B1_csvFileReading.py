class CSVFileReading:
    def __init__(self, fileToBeRead):
        self.fileToBeRead = fileToBeRead

    def readPersonalityInsightsCSV(self):
        # ~--- FORMAT FOR PERSONALITYINSIGHTS CSV FILE IS: ---~ #
        # ~--- column 1: Name ---~ #
        # ~--- column 2: Personality Portrait ---~ #

        import csv
        with open('Resources/' + self.fileToBeRead, 'rb') as f:
            reader = csv.reader(f)
            myList = list(reader)
            # print "Personality insights file has been read in.\nFollowing people are available:"
            # for row in range(len(myList)):
            #     print myList[row][0]
            # print '\n'
        return myList
