# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify
import json
import uuid
import os
import pytz

import fire
import fire_logs
import fire_active
import schedules
import settings


app = Flask(__name__)

# FIRING ROUTES

@app.route('/api/start-fire')
def start_fire():
	filename = request.args.get('schedulePath')
	fire.StartFire(filename)
	return jsonify(result=True)

@app.route('/api/stop-fire')
def stop_fire():
	fire.StopFire()
	return jsonify(result=False)

@app.route('/api/get-total-time')
def get_total_time():
	newTime = fire.get_total_time()
	return jsonify(currentTime=newTime[0],totalTime=newTime[1])

@app.route('/api/get-time-estimate')
def GetTimeEstimate():
	filename = request.args.get('schedulePath')
	return jsonify(time=fire.GetTimeEstimate(filename))

@app.route('/api/get-current-segment')
def get_current_segment():
	scheduleName = fire.get_current_schedule_name()
	scheduleStatus = fire.get_current_status()
	segIndex = fire.get_current_segment()

	error = ""
	if scheduleStatus == "error":
		error = fire.get_error_message()

	# time 
	newTime = fire.get_total_time()

	return jsonify(name=scheduleName, status=scheduleStatus, segment=segIndex, currentTime=newTime[0], totalTime=newTime[1], error=error)

# @app.route('/api/get-current-schedule')
# def get_current_schedule():
# 	scheduleName = fire.get_current_schedule_name()
# 	return jsonify(name=scheduleName)

# @app.route('/api/get-current-status')
# def get_current_status():
# 	scheduleStatus = fire.get_current_status()
# 	return jsonify(status=scheduleStatus)

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
	units = settings.settings['units']
	return schedules.create_schedule(units)

@app.route('/api/list-schedules')
def list_schedules():
	return schedules.list_schedules()

@app.route('/api/get-schedule')
def get_schedule():
	filename = request.args.get('schedulePath')

	# resets status from complete to idle when a new schedule is selected
	if fire.status == "complete":
		fire.status = "idle"

	return schedules.get_schedule(filename)

@app.route('/api/save-schedule', methods=['POST'])
def save_schedule():
	scheduleJSON = request.json
	return schedules.save_schedule(scheduleJSON)



@app.route('/api/load-settings')
def load_settings():
	return settings.load_settings()

@app.route('/api/load-status')
def load_status():
	with open ("status.json", "r") as getStatus:
		statusData = json.load(getStatus)
		return jsonify(statusData)

@app.route('/api/load-totals')
def load_totals():
	return fire_logs.load_totals()

@app.route('/api/get-chart')
def api_get_chart():
	return fire_logs.get_chart()

# This is kind of hacky and needs some cleanup
@app.route('/api/save-settings', methods=['POST'])
def save_settings():
	print("Saving Settings:")
	print(request)
	req_data = request.get_json()
	# print(request.data['maxTemp'])
	print(req_data)
	print(req_data['maxTemp'])

	rawData = request.form
	return settings.save_settings(req_data)


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

with app.app_context():
	print(settings.load_settings())
	print(settings.settings['units'])

if __name__ == '__main__':
	app.run(debug=True, port=80, host='0.0.0.0')