# -*- coding: utf-8 -*-
from flask import jsonify
import json
import os
import shutil
import fire

import io_temp
import settings

active = {}
phases = {}

duration = 0
currentSegment = 0

# startTemp = 0

def GetCurrentTemp():
	global phases
	return io_temp.GetTemp(phases['units'])

def GetEstimateTemp(units):
	global phases
	return io_temp.GetTemp(units)


# Convert the ramp, temp, hold schedules to phase segments

# |SEGMENT |SEGMENT |SEGMENT            
# |        |        |                   
# |        |        |   -               
# |  RAMP  |  HOLD  | -/                
# |        |--------|/                  
# |      -/|        |                   
# |    -/  |        |                   
# |  -/    |        |                   
# |-/                                   
# +------------------------- 

def ConvertToSegments():
	global phases
	global active
	# global startTemp
	global duration
	
	phases.clear()
	phases['name'] = active['name']
	phases['units'] = active['units']
	phases['segments'] = []

	# startTemp = 0
	startTemp = GetCurrentTemp()

	duration = 0.0

	for i in range(len(active['segments'])):
		# convert the ramp to segment
		segmentRamp = {}
		
		rampStartTemp = 0
		# set the start temperature of the first segment the actual 
		# temperature of the kiln or the target temperature, whichever is lower
		if i == 0:
			rampStartTemp = min([active['segments'][i]['temp'], startTemp])
		else:
			rampStartTemp = active['segments'][i - 1]['temp']

		segmentRamp['start'] = rampStartTemp
		segmentRamp['end'] = active['segments'][i]['temp']

		rampDuration = abs(segmentRamp['end'] - segmentRamp['start']) / active['segments'][i]['rate']

		duration += rampDuration
		segmentRamp['finished'] = duration
		
		# convert the hold to segment
		segmentHold = {}
		segmentHold['start'] = active['segments'][i]['temp']
		segmentHold['end'] = active['segments'][i]['temp']

		# convert mins to hours
		duration = duration + (active['segments'][i]['hold'] / 60.0)
		segmentHold['finished'] = duration

		# append the ramp and hold segments
		phases['segments'].append(segmentRamp)
		phases['segments'].append(segmentHold)
	
	print("Phases:")
	print(phases)


# used to show estimates of selected schedules before firing them
def GetTimeEstimate(filename):
	print("getting schedule " + filename)
	src_file = os.path.join('schedules', filename)

	with open (src_file, "r") as scheduleData:
		estimateSchedule = json.load(scheduleData)
		print(estimateSchedule)

	startEstimateTemp = GetEstimateTemp(estimateSchedule['units'])
	estimateDuration = 0.0

	for i in range(len(estimateSchedule['segments'])):

		rampStartTemp = 0
		# set the start temperature of the first segment the actual 
		# temperature of the kiln or the target temperature, whichever is lower
		if i == 0:
			rampStartTemp = min([estimateSchedule['segments'][i]['temp'], startEstimateTemp])
		else:
			rampStartTemp = estimateSchedule['segments'][i - 1]['temp']

		segmentStart = rampStartTemp
		segmentEnd = estimateSchedule['segments'][i]['temp']
		rampDuration = abs(segmentEnd - segmentStart) / estimateSchedule['segments'][i]['rate']
		estimateDuration += rampDuration

		# convert mins to hours
		estimateDuration += estimateSchedule['segments'][i]['hold'] / 60.0
	
	return estimateDuration



def GetTargetTemp(timeHours):
	global phases
	global currentSegment

	if timeHours > phases['segments'][len(phases['segments']) - 1]['finished']:
		print("FINISHED")
		return 0.0

	# get the index of the segment
	segmentIndex = 0
	for i in range(len(phases['segments'])):
		if timeHours <= phases['segments'][i]['finished']:
			segmentIndex = i
			break

	print("index = " + str(segmentIndex) + ", hour = " + str(timeHours))

	# get the start time of the segment
	startTime = 0
	if segmentIndex != 0:
		startTime = phases['segments'][i - 1]['finished']

	# convert time to a percentage of how far it is between the start and end times
	percent = (timeHours - startTime) / (phases['segments'][segmentIndex]['finished'] - startTime)
	
	# find the difference between the segment start and end temperatures, 
	# and then multiply that by the time percentage and add to the start temperature to get the target temperature
	diff = phases['segments'][segmentIndex]['end'] - phases['segments'][segmentIndex]['start']
	temp = phases['segments'][segmentIndex]['start'] + (diff * percent)

	currentSegment = segmentIndex // 2

	return temp


def StartFire(filename):
	global active

	# Copy selected schedule to active
	print("getting schedule " + filename)
	src_file = os.path.join('schedules', filename)
	shutil.copyfile(src_file, "active.json")

	print("READING ACTIVE.JSON")
	with open ('active.json', "r") as activeData:
		active = json.load(activeData)
		print(active)

	ConvertToSegments()

	# fire.start_fire()
	return jsonify(result=True)
