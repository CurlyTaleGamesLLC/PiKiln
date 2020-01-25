# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
import pytz
import time
import threading
import random

# import sensors


fireSchedule = json.dumps('{"placeholder":true}')
fireScheduleLoaded = False
fireScheduleName = ""
fireStatus = "firing"
fireScheduleUnits = "fahrenheit"

# targetTemp = 0
# currentTemp = 0
fireStartTemp = 100
fireCurrentTemp = 100

offset = 0

fireProgressTime = 0
firePhaseLength = 300
firePhaseIndex = 0
fireSegmentIndex = 0
fireTotalLength = 0

fireStartTime = time.time()
stop_threads = False

def get_current_temperature():
	return random.randrange(50,100)

def get_current_units():
	return fireScheduleUnits

def get_current_segment():
	return fireSegmentIndex

def get_current_schedule_name():
	return fireScheduleName

def get_current_status():
	return fireStatus

def get_total_time():
	global fireSchedule
	global fireStartTemp
	global fireTotalLength
	global fireProgressTime

	load_schedule()

	# fireTotalLength = total_time(fireSchedule, fireStartTemp)
	fireTotalLength = get_schedule_time(fireSchedule, fireStartTemp, -1)
	
	return fireProgressTime, fireTotalLength

# returns number of seconds in all of the phases of a firing schedule, or just a single phase with segmentIndex
def get_schedule_time(schedule, startTemp, segmentIndex):
	schedule_time = 0.0
	phase_time = 0.0
	lastTemp = float(startTemp)

	# add time for each phase of each segment
	for i in range(len(schedule['segments']) * 2):
		newIndex = int((i - (i % 2))/2)

		if i % 2 == 0:
			# print("RAMPING")
			rate = schedule['segments'][newIndex]['rate']
			target = schedule['segments'][newIndex]['temp']
			phase_time = get_ramp_time(rate, target, lastTemp)
		else:
			# print("HOLDING")
			phase_time = float(schedule['segments'][newIndex]['hold'])

		# only return a single phase time of a segment
		if segmentIndex == i:
			return phase_time * 60.0

		schedule_time += phase_time

		lastTemp = float(schedule['segments'][newIndex]['temp'])

	return schedule_time * 60.0

# how long it will take to get to the target phase in minutes
def get_ramp_time(rate, target, lastTemp):
	phaseDifference = float(target) - lastTemp
	return abs((float(phaseDifference) / float(rate) * 60.0))


# Main loop that sets temperature of kiln based on schedule and current temp
def schedule_loop():
	global firePhaseIndex
	global fireSegmentIndex
	global fireStartTemp
	global fireStartTime
	global firePhaseLength
	global fireSchedule
	global fireProgressTime
	global fireStatus
	global fireCurrentTemp
	global fireTotalLength
	global offset
	
	firingComplete = False
	isStartTempSet = False
	fireProgressTime = 0
	logTime = 60
	firePhaseIndex = 0

	# speed used to simulate schedules faster
	speed = 60.0 * 5
	speed = 1.0

	phaseStartTime = time.time()
	phaseStartTemp = fireCurrentTemp

	actualTime = 0


	while not firingComplete:

		global stop_threads 
		if stop_threads: 
			print("THREAD STOPPED")
			break

		currentTime = time.time()

		fireProgressTime = float(currentTime-fireStartTime) * speed

		# set the temperature to the correct value based on the segments in the firing schedule
		# print("segments = " + str(len(fireSchedule['segments'])))

		# Each segment has a ramp and a hold phase, so the number of phases is twice the number of segments
		if firePhaseIndex < ((len(fireSchedule['segments'])) * 2):

			if not isStartTempSet:
				fireStartTemp = 0
				isStartTempSet = True
	
			# How many seconds have gone by in this segment phase
			phaseTime = float(currentTime-phaseStartTime) * speed

			phaseLength = get_schedule_time(fireSchedule, fireStartTemp, firePhaseIndex)
			# multiply by speed?

			# what percentage the phase is complete
			if phaseLength == 0:
				rampPercent = 1.0
			else:
				rampPercent = float(phaseTime) / float(phaseLength)

			# how many degrees to the segment target temperature
			newIndex = int((firePhaseIndex - (firePhaseIndex % 2))/2)
			fireSegmentIndex = int(firePhaseIndex/2)
			phaseTemp = fireSchedule['segments'][newIndex]['temp']
			phaseDifference = phaseTemp - phaseStartTemp

			if newIndex % 2 == 0:
				print("RAMPING")
			else:
				print("HOLDING")

			# based on the starting temperature, and how far along we are in the phase set the target temperature
			targetTemp = phaseStartTemp + (rampPercent * phaseDifference)
			
			# this would be reading from the temperature sensor, just get the value from the target temp for now
			fireCurrentTemp = targetTemp - offset
			
			print("phase index = " + str(firePhaseIndex) + " " + str(phaseTime) + "/" + str(phaseLength) + "   " + str(fireProgressTime) + "/" + str(fireTotalLength))

			# To Do: Add GPIO Relay Temperature Control

			# Log Temperature
			logTime += 1
			if logTime  > 14:
				logTime = 0
				print("LOGGING " + str(fireCurrentTemp) + " " + str(targetTemp))
				log_add_data(fireCurrentTemp, targetTemp)
				# add amp sensor reading to log

			# Check if segment phase has completed
			if phaseTime > phaseLength:
				print("Segment Phase Complete")
				actualTime += phaseTime
				phaseStartTime = time.time()
				phaseStartTemp = fireCurrentTemp
				firePhaseIndex += 1	
		else:
			print("FIRING COMPLETE")
			fireStatus = "complete"
			firingComplete = True

		time.sleep(1)

def load_schedule():
	global fireSchedule
	global fireScheduleLoaded

	if not fireScheduleLoaded:
		fireScheduleLoaded = True
		print("READING ACTIVE.JSON")
		with open ('active.json', "r") as fileData:
				fireSchedule = json.load(fileData)
				print(fireSchedule)
				
				# update_status_data(
				# 	fireSchedule['name'],
				# 	"firing",
				# 	"",
				# 	fireSchedule['units'],
				# 	tzone
				# 	)


def start_fire():
	print("FIRING!")

	global fireSchedule
	global fireStartTemp
	global fireCurrentTemp
	global fireStartTime
	global fireThread
	global stop_threads
	global fireScheduleLoaded
	global fireStatus
	global offset

	fireStartTemp = 100
	fireCurrentTemp = 100
	fireStartTime = time.time()

	# Load Settings
	print("READING SETTINGS.JSON")
	with open('settings.json') as json_file:
		data = json.load(json_file)
		tzone = data['notifications']['timezone']
		print(tzone)

		offset = float(data['offset-temp'])

		fireScheduleLoaded = False
		load_schedule()

		# Sets up log file for current schedule
		log_data(fireSchedule['name'], fireSchedule['units'], tzone, fireTotalLength)
	
		# Start a Thread to allow firing sequence to run in the background
		stop_threads = False
		fireStatus = "firing"
		fireThread = threading.Thread(target = schedule_loop) 
		fireThread.start() 
		# schedule_loop()

def stop_fire():
	global fireThread
	global stop_threads
	global fireStatus

	stop_threads = True
	try:
		fireThread.join() 
	except NameError:
		print("well, it WASN'T defined after all!")

	# if fireThread.isAlive():
		
	fireStatus = "canceled"
	print('thread killed') 

#  def update_status_temp(statusTemp):

# def update_status_data(statusName, statusStatus, statusError, statusUnits, statusTimezone):
	
# 	global fireScheduleName
# 	global fireScheduleUnits

# 	print("READING STATUS.JSON")
# 	with open ('status.json', "r") as fileData:
# 		jsonFileData = json.load(fileData)
# 		jsonFileData['name'] = statusName
# 		jsonFileData['error'] = statusError
# 		jsonFileData['units'] = statusUnits
# 		jsonFileData['timezone'] = statusTimezone

# 		fireScheduleName = statusName
# 		fireScheduleUnits = statusUnits

# 		# current date and time
# 		nowTime = datetime.now(tz=pytz.timezone(statusTimezone))
# 		timestamp = nowTime.strftime("%Y-%m-%d %H:%M:%S")
# 		print (timestamp)

# 		jsonFileData['start-time'] = timestamp

# 	print("WRITING STATUS.JSON")
# 	with open('status.json', 'w') as f:
# 		json.dump(jsonFileData, f, indent=4, separators=(',', ':'), sort_keys=True)
# 		#add trailing newline for POSIX compatibility
# 		f.write('\n')

def log_data(logName, logUnits, logTimezone, logTotalTime):

	print ("SET UP LOG FILE")
	logDataJSON = {}
	logDataJSON['name'] = logName
	logDataJSON['error'] = ""
	logDataJSON['units'] = logUnits
	logDataJSON['timezone'] = logTimezone
	logDataJSON['total-time'] = logTimezone
	logDataJSON['temp-log'] = []
	logDataJSON['schedule-log'] = []

	# current date and time
	nowTime = datetime.now(tz=pytz.timezone(logTimezone))
	timestamp = nowTime.strftime("%Y-%m-%d %H:%M:%S")
	print (timestamp)

	logDataJSON['start-time'] = timestamp

	with open('log.json', 'w') as f:
		json.dump(logDataJSON, f, indent=4, separators=(',', ':'), sort_keys=True)
		#add trailing newline for POSIX compatibility
		f.write('\n')

# reads log.json and adds new temp to temp-log
def log_add_data(newTemp, scheduledTemp):

	with open ('log.json', "r") as fileData:
		jsonFileData = json.load(fileData)
		jsonFileData['temp-log'].append(newTemp)
		jsonFileData['schedule-log'].append(scheduledTemp)

	with open('log.json', 'w') as f:
		json.dump(jsonFileData, f, indent=4, separators=(',', ':'), sort_keys=True)
		#add trailing newline for POSIX compatibility
		f.write('\n')

# COST ESTIMATION
# Find the cooldown rate from normal firing
# When the element is on measure the heating rate
# Measure the heating rate based on what temperature it already is
# Create a polynomial from the heating and cooling rates and time