# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify
import json
import shutil
import uuid
import os
import fire

units = True

def str2bool(v):
	return v.lower() in ("yes", "true", "t", "1")

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

app = Flask(__name__)

@app.route('/api/start-fire')
def api_start_fire():
	# fire.hello()

	# Copy selected schedule to active
	print(request)
	filename = request.args.get('schedulePath')
	print("getting schedule " + filename)

	src_file = os.path.join('schedules', filename)
	shutil.copyfile(src_file, "active.json")

	fire.start_fire()
	return jsonify(result=True)

@app.route('/api/stop-fire')
def api_stop_fire():
	# fire.hello_stop()
	fire.stop_fire()
	return jsonify(result=False)

@app.route('/api/get-total-time')
def api_get_total_time():
	newTime = fire.get_total_time()
	return jsonify(currentTime=newTime[0],totalTime=newTime[1])

@app.route('/api/get-current-segment')
def api_get_current_segment():
	segIndex = fire.get_current_segment()
	return jsonify(segment=segIndex)

@app.route('/api/get-current-schedule')
def api_get_current_schedule():
	scheduleName = fire.get_current_schedule_name()
	return jsonify(name=scheduleName)

@app.route('/api/get-current-status')
def api_get_current_status():
	scheduleStatus = fire.get_current_status()
	return jsonify(status=scheduleStatus)

@app.route('/api/temperature')
def api_temp():
	# print("getting temperature" + str(fire.get_current_temperature()))
	currentTemp = fire.get_current_temperature()
	currentUnits = fire.get_current_units()
	return jsonify(temp=currentTemp,units=currentUnits)

@app.route('/api/duplicate-schedule', methods=['POST'])
def duplicate_schedule():
	# import file and create a unique filename
	
	filename = request.form.get('schedulePath')
	src_file = os.path.join('schedules', filename)
	print(src_file)
	unique_filename = str(uuid.uuid4()) + ".json"
	dst_file = os.path.join('schedules', unique_filename)
	print(dst_file)
	
	# update path in imported schedule to be new filename
	with open (src_file, "r") as fileData:
		jsonFileData = json.load(fileData)
		jsonFileData['path'] = unique_filename
		newName = jsonFileData['name'] + ' (new)'
		jsonFileData['name'] = newName

	with open(dst_file, 'w') as f:
		json.dump(jsonFileData, f, indent=4, separators=(',', ':'), sort_keys=True)
		#add trailing newline for POSIX compatibility
		f.write('\n')
	return jsonify(filename=unique_filename,name=jsonFileData['name'])

@app.route('/api/delete-schedule', methods=['DELETE'])
def delete_schedule():
	filename = request.args.get('schedulePath')
	print("deleting schedule " + filename)
	fullPath = os.path.join('schedules', filename)
	os.remove(fullPath)
	return jsonify(result=True)


@app.route('/api/import-schedule', methods=['POST'])
def import_schedule():
	# import file and create a unique filename
	unique_filename = str(uuid.uuid4())
	try:
		file = request.files['imported-schedule']
	except:
		file = None

	# check if valid file
	if file and file.filename.endswith('.json'):
		filename = unique_filename + '.json'
		fullPath = os.path.join('schedules', filename)
		print("saving " + fullPath)
		file.save(fullPath)
		file_uploaded = True
	else:
		filename = None
		file_uploaded = False

	# update path in imported schedule to be new filename
	if file_uploaded:
		with open (fullPath, "r") as fileData:
				jsonFileData = json.load(fileData)
				jsonFileData['path'] = filename

		with open(fullPath, 'w') as f:
			json.dump(jsonFileData, f, indent=4, separators=(',', ':'), sort_keys=True)
			#add trailing newline for POSIX compatibility
			f.write('\n')

	# return some json to reload the page
	jsonResult = str(file_uploaded).lower()
	return jsonify(result=jsonResult)

@app.route('/api/create-schedule', methods=['POST'])
def create_schedule():
	get_units()
	unique_filename = str(uuid.uuid4())
	print("new schedule " + unique_filename)

	newData = {}
	newData['name'] = 'Untitled Schedule'
	newData['units'] = units
	newData['segments'] = []
	newData['segments'].append({'rate':50, 'temp':500,'hold':30})
	newData['segments'].append({'rate':100, 'temp':800,'hold':60})

	with open('schedules/' + unique_filename + '.json', 'w') as f:
		json.dump(newData, f, indent=4, separators=(',', ':'), sort_keys=True)
		#add trailing newline for POSIX compatibility
		f.write('\n')
	fullFileName = unique_filename + ".json"
	return jsonify(filename=fullFileName)

@app.route('/api/list-schedules')
def api_list_schedules():
	print("getting list of schedules")
	newData = {}
	newData['schedules'] = []

	for filename in os.listdir('schedules'):
		if filename.endswith(".json"):
			fullPath = os.path.join('schedules', filename)
			print("reading " + fullPath)
			with open (fullPath, "r") as fileData:
				print(filename)
				jsonFileData = json.load(fileData) 
				newData['schedules'].append({'path':filename, 'name':jsonFileData['name']})

	print('sorting')
	newData['schedules'] = sorted(newData['schedules'], key = lambda i: i['name']) 
	return jsonify(newData)

@app.route('/api/get-schedule')
def api_get_schedule():
	print(request)
	filename = request.args.get('schedulePath')
	print("getting schedule " + filename)

	fullPath = os.path.join('schedules', filename)
	
	with open (fullPath, "r") as fileData:
			jsonFileData = json.load(fileData)

			for index, segment in enumerate(jsonFileData['segments']):
				print(index, segment)
				jsonFileData['segments'][index]['rate'] = segment['rate']
				jsonFileData['segments'][index]['temp'] = segment['temp']
				print(index, segment)
		
			return jsonify(jsonFileData)

	return jsonify(result=False)

@app.route('/api/save-schedule', methods=['POST'])
def save_schedule():
	testJson = request.json
	fullPath = os.path.join('schedules', request.json['path'])

	with open(fullPath, 'w') as f:

		# Convert to degrees C/F
		for segment in testJson['segments']:
			# print("RATE")
			# print(segment['rate'])
			segment['rate'] = segment['rate']
			# print("TEMP")
			# print(segment['temp'])
			segment['temp'] = segment['temp']

		json.dump(testJson, f, indent=4, separators=(',', ':'), sort_keys=True)
		#add trailing newline for POSIX compatibility
		f.write('\n')

	return jsonify(result=True)


@app.route('/api/load-settings')
def api_load_settings():
	print("getting settings")
	with open ("settings.json", "r") as getSettings:
		settingsData = json.load(getSettings)
		print(settingsData)
		return jsonify(settingsData)

@app.route('/api/load-status')
def api_load_status():
	with open ("status.json", "r") as getStatus:
		statusData = json.load(getStatus)
		return jsonify(statusData)

@app.route('/api/load-totals')
def api_load_totals():
	with open ("totals.json", "r") as getTotals:
		totalsData = json.load(getTotals)
		return jsonify(totalsData)

# This is kind of hacky and needs some cleanup
@app.route('/api/update-settings', methods=['POST'])
def update_settings():
	global units
	rawData = request.form

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

@app.route('/api/get-chart')
def api_get_chart():
	with open ("log.json", "r") as getStatus:
		statusData = json.load(getStatus)
		return jsonify(statusData)


# gets most up to date temperature units in settings
def get_units():
	global units
	with open('settings.json') as settings_file:
		data = json.load(settings_file)
		units = data['units']

# render html templates
@app.route('/')
def render_home():
	return render_template('index.html')

@app.route('/index')
def render_home2():
	return render_template('index.html')

@app.route('/firing-schedules')
def render_firing_schedules():
	return render_template('firing-schedules.html')

@app.route('/settings')
def render_settings():
	return render_template('settings.html')

@app.route('/logging')
def render_logging():
	return render_template('logging.html')

# Prevents Caching of pages
@app.after_request
def set_response_headers(response):
	# print("CLEAR CACHE")
	response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '0'
	return response
	
# @app.route('/<string:page_name>')
# def render_static(page_name):
# 	return render_template('%s.html' % page_name)

if __name__ == '__main__':
	get_units()
	app.run(debug=True, port=80, host='0.0.0.0')