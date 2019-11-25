# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
import pytz
import time
import threading
import random


activeSchedule = json.dumps('{"placeholder":true}')
# targetTemp = 0
# currentTemp = 0
startTemp = 15

progressTime = 0
phaseLength = 300
phaseIndex = 0
segmentIndex = 0
totalLength = 0

t0 = time.time()
stop_threads = False


# find the current temperature for the ramp phase or the hold phase of a segment
def current_target(targetTemp, ratePerHour, currentTime, holdTime):
	global startTemp
	global phaseLength
	tempDifference = targetTemp - startTemp
	timeTotalMins = holdTime
	if holdTime == 0:
		timeTotalMins = abs((float(tempDifference) / float(ratePerHour)) * 60)
	rampPercent = float(currentTime) / float(timeTotalMins)
	currentTargetTemp = (rampPercent * tempDifference) + startTemp
	phaseLength = timeTotalMins
	print(currentTargetTemp)
	return currentTargetTemp

def get_current_temperature():
	return random.randrange(50,100)

def get_current_segment():
	return segmentIndex

def get_total_time():
	global activeSchedule
	global startTemp
	global totalLength
	global progressTime

	load_schedule()

	totalLength = 0

	for segment in activeSchedule['segments']:
		# print("seg + " + str(abs(float(segment['temp'] - startTemp))/float(segment['rate']) * 60))
		totalLength += abs((float(segment['temp'] - startTemp)/float(segment['rate'])) * 60)
		# print("hold + " + str(segment['hold']))
		totalLength += segment['hold']

	totalLength = totalLength
	print("totalLength = " + str(totalLength))
	return progressTime, totalLength


def get_phase_data(index):
	global segmentIndex
	newRate = 1
	newHold = 0
	newIndex = (index - (index % 2))/2
	segmentIndex = newIndex
	print("index = " + str(index) + " new index = " + str(newIndex))
	if index % 2 == 0:
		print("RAMPING")
		newRate = activeSchedule['segments'][newIndex]['rate']
	else:
		print("HOLDING")
		newHold = activeSchedule['segments'][newIndex]['hold']
	
	return activeSchedule['segments'][newIndex]['temp'], newRate, newHold


def schedule_loop():
	global phaseIndex
	global startTemp
	global t0
	global phaseLength
	global activeSchedule
	global progressTime
	
	firingComplete = False
	progressTime = 0

	while not firingComplete:

		global stop_threads 
		if stop_threads: 
			print("THREAD STOPPED")
			break

		time.sleep(1)
		t1 = time.time()
		speed = 5

		progressTime += float(t1-t0) * speed

		print("segments = " + str(len(activeSchedule['segments'])))
		if phaseIndex < ((len(activeSchedule['segments'])) * 2):
			
			data = get_phase_data(phaseIndex)
			nowTemp = current_target(data[0], data[1], float(t1-t0) * speed, data[2])

			print("phase index = " + str(phaseIndex) + " " + str(float(t1-t0)) + "/" + str(phaseLength/speed))

			if t1-t0 > phaseLength/speed:
				print("half minute over, (not a precise timing) ")
				t0 = time.time()
				startTemp = nowTemp
				phaseIndex += 1
		else:
			firingComplete = True
			print("FIRING COMPLETE")

def load_schedule():
	global activeSchedule
	tzone = "Etc/GMT+3"

	with open ('active.json', "r") as fileData:
			activeSchedule = json.load(fileData)
			print(activeSchedule)
			
			update_status_data(
				activeSchedule['name'],
				"firing",
				"",
				activeSchedule['units'],
				tzone
				)


def start_fire():
	print("FIRING!")

	global activeSchedule
	global startTemp
	global fireThread
	global stop_threads

	startTemp = 20

	# Load Settings
	with open('settings.json') as json_file:
		data = json.load(json_file)
		tzone = data['notifications']['timezone']
		print(tzone)

		# Load Schedule
		# with open ('active.json', "r") as fileData:
		# 	activeSchedule = json.load(fileData)
		# 	print(activeSchedule)
			
		# 	update_status_data(
		# 		activeSchedule['name'],
		# 		"firing",
		# 		"",
		# 		activeSchedule['units'],
		# 		tzone
		# 		)

		load_schedule()

		# Start a Thread to allow firing sequence to run in the background
		stop_threads = False
		fireThread = threading.Thread(target = schedule_loop) 
		fireThread.start() 
		# schedule_loop()

def stop_fire():
	global fireThread
	global stop_threads
	stop_threads = True
	fireThread.join() 
	print('thread killed') 

#  def update_status_temp(statusTemp):

def update_status_data(statusName, statusStatus, statusError, statusUnits, statusTimezone):
	with open ('status.json', "r") as fileData:
		jsonFileData = json.load(fileData)
		jsonFileData['name'] = statusName
		jsonFileData['status'] = statusStatus
		jsonFileData['error'] = statusError
		jsonFileData['units'] = statusUnits
		jsonFileData['timezone'] = statusTimezone

		# current date and time
		nowTime = datetime.now(tz=pytz.timezone(statusTimezone))
		timestamp = nowTime.strftime("%Y-%m-%d %H:%M:%S")
		print (timestamp)

		jsonFileData['start-time'] = timestamp

	with open('status.json', 'w') as f:
		json.dump(jsonFileData, f, indent=4, separators=(',', ':'), sort_keys=True)
		#add trailing newline for POSIX compatibility
		f.write('\n')

#start_fire()

def hello():
	get_total_time()
	print("Hello World!")

def hello_stop():
	print("Stop Hello World!")

		
		

	

	