import pickle
import pprint

	

def loadConfigTxtFile(configFile):
		
    configTxt = open(configFile, "r").read().splitlines() # Grab contents from config.txt file
    params = []
	
    for word in range(len(configTxt)):
	
        if configTxt[word].startswith('_'): # Grab the useful bits from the file as strings
            newParam = configTxt[word].split(': ')
            newParam[0] = newParam[0][1:]
            try: # Convert the strings to ints/floats if they need to be
                newParam[1] = int(newParam[1])
            except:
                try:
                    newParam[1] = float(newParam[1])
                except:
                    pass
            params.append(newParam)

    configDict = {}
    for i in range(len(params)): # Return the config file in Python dictionary form
        configDict[params[i][0]] = params[i][1]
    return configDict
	




def save_obj(obj, fileName):
		
    with open('Config/' + fileName + ".pkl", 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
	print 'Config/' + fileName + ".pkl", 'wb'



def createConfigFile(configFile):
    configDict = loadConfigTxtFile(configFile)
    save_obj(configDict, "configurationDictionary")
    print "Configuration file updated.\n"

def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)

# --- Test code --- #

#x = loadConfigTxtFile("Robot Configuration.txt")
#pp = pprint.PrettyPrinter(indent=2)
#pp.pprint (x)

