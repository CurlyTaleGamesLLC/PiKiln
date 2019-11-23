from flask import Flask, render_template, request
import json
import uuid
import os

units = True

def str2bool(v):
	return v.lower() in ("yes", "true", "t", "1")

app = Flask(__name__)

@app.route('/api/timezones')
def api_timezones():
	with open ("timezones.txt", "r") as zones:
		zoneData = zones.read()
		return zoneData

@app.route('/api/temperature')
def api_temp():
	print("getting temperature")
	return 'temperature'

@app.route('/api/delete-schedule', methods=['DELETE'])
def delete_schedule():
	filename = request.args.get('schedulePath')
	print("deleting schedule " + filename)
	fullPath = os.path.join('schedules', filename)
	os.remove(fullPath)
	return 'Deleted ' + filename


@app.route('/api/create-schedule', methods=['POST'])
def create_schedule():
	update_units()
	unique_filename = str(uuid.uuid4())
	print("new schedule " + unique_filename)

	newData = {}
	newData['name'] = 'Untitled Schedule'
	newData['segments'] = []
	newData['segments'].append({'rate':50, 'temp':500,'hold':30})
	newData['segments'].append({'rate':100, 'temp':800,'hold':60})

	with open('schedules/' + unique_filename + '.json', 'w') as f:
		json.dump(newData, f, indent=4, separators=(',', ':'), sort_keys=True)
		#add trailing newline for POSIX compatibility
		f.write('\n')

	return unique_filename + ".json"

@app.route('/api/list-schedules')
def api_list_schedules():
	print("getting list of schedules")

	newData = {}
	newData['schedules'] = []

	for filename in os.listdir('schedules'):
		fullPath = os.path.join('schedules', filename)
		print("reading " + fullPath)
		with open (fullPath, "r") as fileData:
			print(filename)
			jsonFileData = json.load(fileData) #'\\schedules\\' + 
			newData['schedules'].append({'path':filename, 'name':jsonFileData['name']})

	print('sorting')
	newData['schedules'].sort()
	return newData

@app.route('/api/get-schedule')
def api_get_schedule():
	update_units()
	
	filename = request.args.get('schedulePath')
	print("getting schedule " + filename)

	fullPath = os.path.join('schedules', filename)
	
	with open (fullPath, "r") as fileData:
			jsonFileData = json.load(fileData)

			for index, segment in enumerate(jsonFileData['segments']):
				print(index, segment)
				jsonFileData['segments'][index]['rate'] = tempValue(segment['rate'])
				jsonFileData['segments'][index]['temp'] = tempValue(segment['temp'])
				print(index, segment)

			# Convert to degrees C/F
			# for segment in jsonFileData['segments']:
			# 	print("RATE")
			# 	print(segment['rate'])
			# 	segment['rate'] = tempValue(segment['rate'])
			# 	print(segment['rate'])
			# 	print("TEMP")
			# 	print(segment['temp'])
			# 	segment['temp'] = tempValue(segment['temp'])
			# 	print(segment['temp'])

			
			
			return jsonFileData
	return 'No Schedule'

@app.route('/api/save-schedule', methods=['POST'])
def save_schedule():
	update_units()
	testJson = request.json
	fullPath = os.path.join('schedules', request.json['path'])

	with open(fullPath, 'w') as f:

		# Convert to degrees C/F
		for segment in testJson['segments']:
			print("RATE")
			print(segment['rate'])
			segment['rate'] = tempValueWrite(segment['rate'])
			print(segment['rate'])
			print("TEMP")
			print(segment['temp'])
			segment['temp'] = tempValueWrite(segment['temp'])
			print(segment['temp'])

		json.dump(testJson, f, indent=4, separators=(',', ':'), sort_keys=True)
		#add trailing newline for POSIX compatibility
		f.write('\n')

	return 'saved'


@app.route('/api/load-settings')
def api_load_settings():
	update_units()
	print("getting settings")
	with open ("settings.json", "r") as getSettings:
		settingsData = json.load(getSettings)
		print(settingsData)
		settingsData['max-temp'] = tempValue(settingsData['max-temp'])
		print(settingsData)
		return settingsData

@app.route('/api/update-settings', methods=['POST'])
def update_settings():
	global units
	rawData = request.form
	
	newData = {}
	newData['notifications'] = {}
	newData['notifications']['timezone'] = rawData['timezone']
	newData['notifications']['sender'] = rawData['sender']
	newData['notifications']['sender-password'] = rawData['sender-password']
	newData['notifications']['receiver'] = rawData['receiver']
	newData['notifications']['enable-email'] = str2bool(rawData['enable-email'])

	
	newData['units'] = rawData['units']
	# bug here with max temp and units
	units = newData['units'] == "celsius"
	newData['max-temp'] = tempValueWrite(float(rawData['max-temp']))
	newData['cost'] = float(rawData['cost'])
	
	with open('settings.json', 'w') as f:
		json.dump(newData, f, indent=4, separators=(',', ':'), sort_keys=True)
		#add trailing newline for POSIX compatibility
		f.write('\n')
		#return render_template('settings.html')
	return request.form
	# return render_template('settings.html')

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

@app.after_request
def set_response_headers(response):
	print("CLEAR CACHE")
	response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '0'
	return response

def tempValue(value):
	global units
	if units:
		return value
	else:
		return value * 9 / 5 + 32

def tempValueWrite(value):
	global units
	if units:
		return value
	else:
		return (value -32) * 5 / 9
	
def update_units():
	global units
	with open('settings.json') as settings_file:
		data = json.load(settings_file)
		units = data['units'] == "celsius"
		print("is celsius")
		print(units)

	
# @app.route('/<string:page_name>')
# def render_static(page_name):
# 	return render_template('%s.html' % page_name)

if __name__ == '__main__':
	update_units()
	app.run(debug=True, host='0.0.0.0')