from flask import jsonify
import json
import uuid
import os

def create_schedule(units):
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

def duplicate_schedule(filename):
	# import file and create a unique filename
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

def delete_schedule(filename):
	# filename = request.args.get('schedulePath')
	print("deleting schedule " + filename)
	fullPath = os.path.join('schedules', filename)
	os.remove(fullPath)
	return jsonify(result=True)

def import_schedule(file):
	# import file and create a unique filename
	unique_filename = str(uuid.uuid4())

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

def list_schedules():
	print("getting list of schedules")
	newData = []
	# newData = {}
	# newData['schedules'] = []

	for filename in os.listdir('schedules'):
		if filename.endswith(".json"):
			fullPath = os.path.join('schedules', filename)
			print("reading " + fullPath)
			with open (fullPath, "r") as fileData:
				print(filename)
				jsonFileData = json.load(fileData) 
				newData.append({'path':filename, 'name':jsonFileData['name']})

	print('sorting')
	newData = sorted(newData, key = lambda i: i['name']) 
	return jsonify(newData)

def get_schedule(filename):
	# print(request)
	# filename = request.args.get('schedulePath')
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

# writes schedule to disk
def save_schedule(scheduleJSON):
	# scheduleJSON = request.json
	fullPath = os.path.join('schedules', scheduleJSON['path'])

	with open(fullPath, 'w') as f:

		# Convert to degrees C/F
		# I think i can get rid of this. temperatures are now stored in native units
		for segment in scheduleJSON['segments']:
			segment['rate'] = segment['rate']
			segment['temp'] = segment['temp']

		json.dump(scheduleJSON, f, indent=4, separators=(',', ':'), sort_keys=True)
		#add trailing newline for POSIX compatibility
		f.write('\n')

	return jsonify(path=scheduleJSON['path'])