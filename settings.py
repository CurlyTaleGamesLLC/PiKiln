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

def save_settings(rawData):
	global settings
	print(rawData)
		
	# write new settings to json file
	with open('settings.json', 'w') as f:
		json.dump(rawData, f, indent=4, separators=(',', ':'), sort_keys=True)
		#add trailing newline for POSIX compatibility
		f.write('\n')

	settings = rawData

	return jsonify(result=True)

def load_settings():
	global settings
	print("getting settings")
	with open ("settings.json", "r") as getSettings:
		settingsData = json.load(getSettings)
		print(settingsData)
		settings = settingsData
		# return "Loaded Settings"
		return jsonify(settingsData)