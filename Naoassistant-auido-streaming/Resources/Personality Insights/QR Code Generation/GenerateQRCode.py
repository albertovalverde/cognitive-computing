import os
from subprocess import call

# Generates QR codes based on the names of pictures in the database.

def GenerateQRCode(QRcodetext):
    call('qr ' + QRcodetext + ' > "QR codes/' + QRcodetext +'.png"', shell = True)

print 'Select the folder containing the images of people you need QR codes for. It is assumed that the folder is sitting in the \'Pictures of Analysed People\' folder. You can also just hit enter to let it search for files in the \'Pictures of Analysed People\' folder.'
folderName = raw_input()
if folderName != '':
    folderName = '/' + folderName

folderPath = '../Pictures of Analysed People' + folderName

for fileName in os.listdir(folderPath):
    fileName = os.path.splitext(fileName)[0]
    print 'Processing ', fileName
    GenerateQRCode(fileName)
