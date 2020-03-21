# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
import json
import uuid
import os

units = True

def is_json_key_present(json, key):
	try:
		buf = json[key]
	except KeyError:
		return False
	return True

def update_settings(rawData):
	global units
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

	# convert max temp if units were changed
	isFahrenheit = is_json_key_present(rawData, 'units')
	newData['units'] = "fahrenheit" if isFahrenheit else "celsius"

	newData['max-temp'] = float(rawData['max-temp'])
	if units != newData['units']:
		if units == "celsius":
			newData['max-temp'] = float(rawData['max-temp']) * 9 / 5 + 32
		else:
			newData['max-temp'] = (float(rawData['max-temp']) -32) * 5 / 9

	newData['offset-temp'] = float_default(float(rawData['offset-temp']), 0.0)

	units = newData['units']
		
	# write new settings to json file
	with open('settings.json', 'w') as f:
		json.dump(newData, f, indent=4, separators=(',', ':'), sort_keys=True)
		#add trailing newline for POSIX compatibility
		f.write('\n')
	return jsonify(result=True)

def load_settings():
	print("getting settings")
	with open ("settings.json", "r") as getSettings:
		settingsData = json.load(getSettings)
		print(settingsData)
		return jsonify(settingsData)

def get_units():
	# global units
	# with open('settings.json') as settings_file:
	# 	data = json.load(settings_file)
	# 	units = data['units']

	with open('settings.json') as settings_file:
		data = json.load(settings_file)
		units = data['units']
		return units