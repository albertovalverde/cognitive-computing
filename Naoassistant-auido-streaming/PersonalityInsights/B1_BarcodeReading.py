from naoqi import ALProxy
import time

class BarcodeReading:
    def __init__(self, IP, PORT, robotCheck):
        # ~--- Prepare Naomi for demo ---~#
        if robotCheck:
            self.tts = ALProxy("ALTextToSpeech", IP, PORT)
            self.ttsa = ALProxy("ALAnimatedSpeech", IP, PORT)
            self.bar = ALProxy("ALBarcodeReader", IP, PORT)
            self.mem = ALProxy("ALMemory", IP, PORT)
            self.tts.setParameter("speed", 92)
        self.printClassCreationSuccess()

    def printClassCreationSuccess(self):
        print "Barcode reading class successfully initialised.\n"

    def readBarcode(self):
        self.bar.subscribe("check_barcode")
        for i in range(50):
            self.mem.getDataList("BarcodeReader")
            data = self.mem.getData("BarcodeReader/BarcodeDetected")
            print "Barcode result is: " + str(data)
            try:
                if len(data) > 0:
                    self.tts.say("That's " + str(data[0][0]) + "! Great choice!")
                    break
            except:
                if data != None:
                    self.ttsa.say("Thank you, I've recognised your QR code!")
                    break
            if i == 49:
                self.ttsa.say("Woops, I couldn't recognise your QR code.")
                return 0
            time.sleep(0.2)
        return data[0][0]
