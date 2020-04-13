# -*- coding: utf-8 -*-
from flask import jsonify
import json
import os
from datetime import datetime
import pytz
import time

import threading
import random

import settings

log = {}
logCounter = 0

def StartLog(logName, logUnits):

	global log

	print ("SET UP LOG FILE")
	logDataJSON = {}
	logDataJSON['name'] = logName
	logDataJSON['error'] = ""
	logDataJSON['units'] = logUnits
	logDataJSON['tempLog'] = []
	logDataJSON['scheduleLog'] = []

	# current date and time
	nowTime = datetime.now()
	timestamp = nowTime.strftime("%Y-%m-%d %H:%M:%S")
	print (timestamp)

	logDataJSON['startTime'] = timestamp
	
	log = logDataJSON
	WriteLog()

# reads log.json and adds new temp to temp-log
def AddData(newTemp, scheduledTemp):

	global log
	global logCounter

	log['tempLog'].append(newTemp)
	log['scheduleLog'].append(scheduledTemp)

	# limit the number of disk writes, with a duty cycle of 4 seconds this works out to every 5 mins
	logCounter = logCounter + 1
	if logCounter > 15:
		logCounter = 0
		WriteLog()

	

def WriteLog():
	global log
	with open('log.json', 'w') as f:
		json.dump(log, f, indent=4, separators=(',', ':'), sort_keys=True)
		#add trailing newline for POSIX compatibility
		f.write('\n')

	
def get_chart():
	with open ("log.json", "r") as getStatus:
		statusData = json.load(getStatus)
		return jsonify(statusData)

def load_totals():
	with open ("totals.json", "r") as getTotals:
		totalsData = json.load(getTotals)
		return jsonify(totalsData)

def UpdateTotals(fireAmps, fireTime):
	with open ("totals.json", "r") as getTotals:
		totalsData = json.load(getTotals)

		print("before:")
		print(totalsData)

		# convert amps used in fire to kilowatts multiplied by the cot per kilowatt
		fireCost = ((fireAmps * settings.settings['volts']) / 1000.0) * settings.settings['cost']
		print("Fire Cost: " + str(fireCost))

		totalsData['fires'] += 1
		totalsData['cost'] += fireCost
		totalsData['time'] += fireTime

		print("after:")
		print(totalsData)

	with open('totals.json', 'w') as f:
		json.dump(totalsData, f, indent=4, separators=(',', ':'), sort_keys=True)
		#add trailing newline for POSIX compatibility
		f.write('\n')


# COST ESTIMATION
# Find the cooldown rate from normal firing
# When the element is on measure the heating rate
# Measure the heating rate based on what temperature it already is
# Create a polynomial from the heating and cooling rates and time