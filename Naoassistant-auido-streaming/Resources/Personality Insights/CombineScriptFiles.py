import os
datastring = ''
doof = ''
mydict = {}
print "Which folder are you interested in, select the number"
i = 1
for folder in os.listdir('.'):
    print i, folder
    mydict[i] = folder
    i+=1
doof = raw_input()
doof = mydict[int(doof)]

for filename in os.listdir(doof):
    openFile = open(doof + '/' + filename)
    contents = openFile.read()
    datastring += contents
    openFile.close

combinedtextfile = open(doof + '_combined.txt', 'w')
combinedtextfile.write(datastring)
combinedtextfile.close()
print 'done'
