# -*- coding: utf-8 -*-
from flask import jsonify
import json
import uuid
import os

settings = {}

def is_json_key_present(json, key):
	try:
		buf = json[key]
	except KeyError:
		return False
	return True

def float_default(n,d):
    try:
        return float(n)
    except ValueError:
        return d

def int_default(n,d):
    try:
        return int(n)
    except ValueError:
        return d

def str2bool(v):
	return v.lower() in ("yes", "true", "t", "1")

def update_settings(rawData):
	global settings
	print(rawData)

	# reformat data from form
	newData = {}
	newData['notifications'] = {}
	newData['notifications']['timezone'] = rawData['timezone']
	newData['notifications']['sender'] = rawData['sender']
	newData['notifications']['sender-password'] = rawData['sender-password']
	newData['notifications']['receiver'] = rawData['receiver']
	# form has to send checked value of on in order for enable-email to have any value
	newData['notifications']['enable-email'] = is_json_key_present(rawData, 'enable-email')
	newData['cost'] = float(rawData['cost'])
	newData['volts'] = float(rawData['volts'])

	isFahrenheit = is_json_key_present(rawData, 'units')
	newData['units'] = "fahrenheit" if isFahrenheit else "celsius"

	newData['max-temp'] = float(rawData['max-temp'])
	newData['offset-temp'] = float_default(float(rawData['offset-temp']), 0.0)
		
	# write new settings to json file
	with open('settings.json', 'w') as f:
		json.dump(newData, f, indent=4, separators=(',', ':'), sort_keys=True)
		#add trailing newline for POSIX compatibility
		f.write('\n')

	settings = newData

	return jsonify(result=True)

def load_settings():
	global settings
	print("getting settings")
	with open ("settings.json", "r") as getSettings:
		settingsData = json.load(getSettings)
		print(settingsData)
		settings = settingsData
		return jsonify(settingsData)