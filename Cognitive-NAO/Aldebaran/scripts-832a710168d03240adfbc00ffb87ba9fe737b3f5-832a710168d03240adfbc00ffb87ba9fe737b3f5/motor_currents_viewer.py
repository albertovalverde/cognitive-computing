import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import time
import random
from naoqi import ALProxy
from threading import Thread
from math import factorial


class EventThread(Thread):
	"""
	Thread class allowing the user to stop the main
	loop
	"""

	def __init__(self):
		"""
		Constructor
		"""
		Thread.__init__(self)
		self.stopLoop = False

	def checkLoopState(self):
		"""
		Getter to get the stop loop var
		"""
		return self.stopLoop

	def run(self):
		"""
		The run method
		"""
		try:
			sys.stdin.readline()

		except KeyboardInterrupt:
			pass

		finally:
			self.stopLoop = True



def savitzkyGolay(y, windowSize, order, deriv=0, rate=1):
	"""
	Savitsky Golay filter
	"""
	try:
		windowSize = np.abs(np.int(windowSize))
		order = np.abs(np.int(order))
	
	except ValueError, msg:
		raise ValueError("windowSize and order have to be of type int")
	
	if windowSize % 2 != 1 or windowSize < 1:
		raise TypeError("windowSize size must be a positive odd number")
	
	if windowSize < order + 2:
		raise TypeError("windowSize is too small for the polynomials order")
	
	order_range = range(order+1)
	half_window = (windowSize -1) // 2
	
	# Precompute coefficients
	b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
	m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
	
	# Pad the signal at the extremes with
	# Values taken from the signal itself
	firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
	lastvals  = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
	y         = np.concatenate((firstvals, y, lastvals))

	return np.convolve( m[::-1], y, mode='valid')



def main():
	"""
	Main method
	"""

	print "#------------------------------------#"
	print "|         Current visualizer         |"
	print "#------------------------------------#"

	try:
		assert len(sys.argv) >= 4

	except AssertionError:
		print "Use this script like this : python motorCurrents.py ip port motorName1 motorName2 ..."
		print "The motorNames are : RWristYaw, ..."
		sys.exit(1)

	IP                 = sys.argv[1]
	PORT               = sys.argv[2]
	currentDictionnary = dict()
	listenedMotorNames = list()
	timeList           = list()
	eventThread        = EventThread()
	data               = None
	start_time         = 0
	nIterations        = 0
	nPlots             = 0
	nGraph             = 0
	figure             = None

	try:
		memoryProxy = ALProxy("ALMemory", str(IP), int(PORT))

	except Exception, e:
		print "-------------------------------------------------------"
		print "An exception occured during the listener initialization"
		print "Error was : ", e
		print "-------------------------------------------------------"
		sys.exit(1)
	
	for i in range(len(sys.argv) - 3):
		listenedMotorNames.append(sys.argv[i+3])

	# Check if the motors exist and initialize the current dictionnary:
	for motorName in listenedMotorNames:
		try:
			memoryProxy.getData("Device/SubDeviceList/" + motorName + "/ElectricCurrent/Sensor/Value")
			currentDictionnary[motorName] = list()

		except Exception, e:
			print "----------------------------------------------------------------"
			print "An exception occured while checking if " + motorName + "existed."
			print "Error was : ", e
			print "----------------------------------------------------------------"


	# Main loop :
	eventThread.start()
	print "Start recording..."
	print "---------------------------------"
	print "Press enter to stop the recording"
	print "---------------------------------"
	start_time = time.time()

	while True:
		nIterations += 1
		timeList.append(time.time() - start_time)

		for motorName in currentDictionnary.keys():
			data = memoryProxy.getData("Device/SubDeviceList/" + motorName + "/ElectricCurrent/Sensor/Value")
			currentDictionnary[motorName].append(data)

		if eventThread.checkLoopState():
			print 'Stop Recording...'
			break

	print "----------------------"
	print "Creating the graphs..."
	print "----------------------"

	figure = plt.figure()
	figure.suptitle('Currents', fontsize=14, fontweight='bold')

	nPlots      = len(currentDictionnary.keys())
	nGraph      = 1

	for motorName in currentDictionnary.keys():
		plt.subplot(nPlots, 1, nGraph)
		plt.plot(timeList, currentDictionnary[motorName], 'b', label="Raw sensor data")
		plt.plot(timeList, savitzkyGolay(np.asarray(currentDictionnary[motorName]), 31, 4), 'r', label="Filtered sensor data")
		plt.title(motorName)
		plt.ylabel("Current (A)")

		if nGraph is 1:
			plt.legend(bbox_to_anchor=(0., 1.35, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.).draggable(True)

		if nGraph is nPlots:
			plt.xlabel("Time (sec)")
		
		nGraph += 1

	plt.show()

if __name__ == "__main__":
	main()

