"""
with sample of python documentation
"""

import os
import sys
import time
import naoqi
from naoqi import ALBroker
from naoqi import ALModule
from naoqi import ALProxy
from naoqi import ALBehavior
from naoqi import ALDocable


# create python module
class myModule(ALModule):
  """python class myModule test auto documentation"""


  def pythondatachanged(self, strVarName, value,message):
    """callback when data change"""
    print "Micro-event is raise callback is called by ALMemory"
    print value
    #print "datachanged", strVarName, " ", value, " ", strMessage



# connect brokers (we suppose naoqi run)
myBroker = naoqi.ALBroker("myBroker",
                          "0.0.0.0",  # listen to anyone
                          0,  # find a free port and use it
                          "192.168.1.36",  # parent broker IP
                          9559)  # parent broker port
print("ok broker")


# don't forget to call all methods in try catch bloc

#we create a proxy without IP adress because be have already connected brokers
memory = ALProxy("ALMemory")
print "[ RUN      ] create python module"

# create an ALModule
pythonModule = myModule("pythonModule")

# subscribe to micro-event to be notified when event is raised
print "Subscribe to micro-event"
memory.subscribeToMicroEvent("myMicroEvent", "pythonModule", "message", "pythondatachanged")

# raise micro-event event
print "raise micro-event"
memory.raiseMicroEvent("myMicroEvent", 42)

time.sleep(200)
