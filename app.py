# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify
import json
import shutil
import uuid
import os
import fire
import fire_logs
import schedules
import settings

units = True

def str2bool(v):
	return v.lower() in ("yes", "true", "t", "1")

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

# FIRING ROUTES

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

# SCHEDULE ROUTES

@app.route('/api/duplicate-schedule', methods=['POST'])
def duplicate_schedule():
	# # import file and create a unique filename
	filename = request.form.get('schedulePath')
	return schedules.duplicate_schedule(filename)

@app.route('/api/delete-schedule', methods=['DELETE'])
def delete_schedule():
	filename = request.args.get('schedulePath')
	return schedules.delete_schedule(filename)


@app.route('/api/import-schedule', methods=['POST'])
def import_schedule():
	try:
		file = request.files['imported-schedule']
	except:
		file = None
	return schedules.import_schedule(file)

@app.route('/api/create-schedule', methods=['POST'])
def create_schedule():
	units = settings.get_units()
	return schedules.create_schedule(units)

@app.route('/api/list-schedules')
def list_schedules():
	return schedules.list_schedules()

@app.route('/api/get-schedule')
def get_schedule():
	filename = request.args.get('schedulePath')
	return schedules.get_schedule(filename)

@app.route('/api/save-schedule', methods=['POST'])
def save_schedule():
	scheduleJSON = request.json
	return schedules.save_schedule(scheduleJSON)



@app.route('/api/load-settings')
def load_settings():
	# print("getting settings")
	# with open ("settings.json", "r") as getSettings:
	# 	settingsData = json.load(getSettings)
	# 	print(settingsData)
	# 	return jsonify(settingsData)
	return settings.load_settings()

@app.route('/api/load-status')
def api_load_status():
	with open ("status.json", "r") as getStatus:
		statusData = json.load(getStatus)
		return jsonify(statusData)

@app.route('/api/load-totals')
def load_totals():
	# with open ("totals.json", "r") as getTotals:
	# 	totalsData = json.load(getTotals)
	# 	return jsonify(totalsData)
	return fire_logs.load_totals()

@app.route('/api/get-chart')
def api_get_chart():
	# with open ("log.json", "r") as getStatus:
	# 	statusData = json.load(getStatus)
	# 	return jsonify(statusData)
	return fire_logs.get_chart()

# This is kind of hacky and needs some cleanup
@app.route('/api/update-settings', methods=['POST'])
def update_settings():
	global units
	rawData = request.form

	# print(rawData)
	
	# # reformat data from form
	# newData = {}
	# newData['notifications'] = {}
	# newData['notifications']['timezone'] = rawData['timezone']
	# newData['notifications']['sender'] = rawData['sender']
	# newData['notifications']['sender-password'] = rawData['sender-password']
	# newData['notifications']['receiver'] = rawData['receiver']
	# # form has to send checked value of on in order for enable-email to have any value
	# newData['notifications']['enable-email'] = is_json_key_present(rawData, 'enable-email')
	# newData['cost'] = float(rawData['cost'])
	# newData['volts'] = float(rawData['volts'])

	# # convert max temp if units were changed
	# isFahrenheit = is_json_key_present(rawData, 'units')
	# newData['units'] = "fahrenheit" if isFahrenheit else "celsius"

	# newData['max-temp'] = float(rawData['max-temp'])
	# if units != newData['units']:
	# 	if units == "celsius":
	# 		newData['max-temp'] = float(rawData['max-temp']) * 9 / 5 + 32
	# 	else:
	# 		newData['max-temp'] = (float(rawData['max-temp']) -32) * 5 / 9

	# newData['offset-temp'] = float_default(float(rawData['offset-temp']), 0.0)

	# units = newData['units']
		
	# # write new settings to json file
	# with open('settings.json', 'w') as f:
	# 	json.dump(newData, f, indent=4, separators=(',', ':'), sort_keys=True)
	# 	#add trailing newline for POSIX compatibility
	# 	f.write('\n')
	return settings.update_settings(rawData)




# gets most up to date temperature units in settings
# def get_units():
# 	global units
# 	with open('settings.json') as settings_file:
# 		data = json.load(settings_file)
# 		units = data['units']

# render html templates
@app.route('/')
def render_home():
	return render_template('index.html')

@app.route('/index')
def render_home_index():
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

if __name__ == '__main__':
	get_units()
	app.run(debug=True, port=80, host='0.0.0.0')