# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
import pytz
import time

import threading
import random


def StartLog(logName, logUnits, logTimezone, logTotalTime):

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
def AddData(newTemp, scheduledTemp):

	with open ('log.json', "r") as fileData:
		jsonFileData = json.load(fileData)
		jsonFileData['temp-log'].append(newTemp)
		jsonFileData['schedule-log'].append(scheduledTemp)

	with open('log.json', 'w') as f:
		json.dump(jsonFileData, f, indent=4, separators=(',', ':'), sort_keys=True)
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

# COST ESTIMATION
# Find the cooldown rate from normal firing
# When the element is on measure the heating rate
# Measure the heating rate based on what temperature it already is
# Create a polynomial from the heating and cooling rates and time