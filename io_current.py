import board
import busio

import time
import threading
import math

#import adafruit_ads1x15.ads1015 as ADS
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
#ads = ADS.ADS1015(i2c)
ads = ADS.ADS1115(i2c)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)

gains = (2/3, 1, 2, 4, 8, 16)
ads.gain = gains[1]

offset = 1.649
threshold = 0.1

totalCurrent = 0
averageCurrent = []
measurementComplete = False


def GetAverageCurrnet():
	global averageCurrent

	# get an average for all the samples
	averageTotal = 0
	for avg in averageCurrent:
		averageTotal += avg
	averageTotal = averageTotal / len(averageCurrent)

	# return the square root of the averaged samples
	return math.sqrt(averageTotal)

def Reset():
	global offset
	global chan

	offset = chan.voltage
	print("OFFSET = " + str(offset))


def IsConnected():
	avg = GetAverageCurrnet()
	if avg > threshold:
		print("Current = True = " + str(avg))
		return True
	else:
		print("Current = False = " + str(avg))
		return False

def CurrentMesurementThread():
	global startTime
	global totalCurrent
	global measurementComplete
	global chan
	global averageCurrent
	global offset
	
	startTime = time.time()
	totalCurrent = 0
	sampleCurrent = 0
	sampleCount = 0
	measurementComplete = False

	print("Starting Current Measurement Thread")

	sampleTime = 0.05
	
	# burden resistor value
	rBurden = 100
	# number of turns of non invasive current sensor
	numTurns = 2000

	offset = 1.65

	while not measurementComplete:
		# Get voltage from ADC, and subtract offset voltage
		sample = float(chan.voltage) - offset
		# Convert ADC voltage to current value
		sample = (sample / rBurden) * numTurns
		# Square the current value
		sampleSquared = (sample * sample)
		
		sampleCurrent += sampleSquared
		sampleCount += 1

		# Keep an updated average of the current
		averageCurrent.append(sampleSquared)
		if len(averageCurrent) > 5:
			averageCurrent.pop(0)


		# Every second log the total current
		if sampleCount > 10:
			totalCurrent += math.sqrt(sampleCurrent / sampleCount)
			sampleCurrent = 0
			sampleCount = 0
			# print("AVG " + str(GetAverageCurrnet()))
			# print("TOT " + str(totalCurrent))

		time.sleep(sampleTime)


def StartMeasurement():
	global currentThread

	# Start a Thread to allow current sensing to run continually run in the background
	
	currentThread = threading.Thread(target = CurrentMesurementThread) 
	currentThread.start()

def StopMeasurement():
	global currentThread
	global measurementComplete
	global totalCurrent

	measurementComplete = True
	try:
		currentThread.join() 
	except NameError:
		print("thread wasn't defined")

	print('current thread killed')

	# convert total current to amp hours
	return totalCurrent / 3600.0


# print(str(GetAverageCurrnet()))
# print(str(IsConnected()))
# CurrentMesurementThread()