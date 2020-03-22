# -*- coding: utf-8 -*-

import json
import os
# from datetime import datetime
# import pytz
import time
import threading

# custom libraries for hardware
import io_relay
import io_temp
import io_current

import fire_logs
import fire_active

import settings

status = "firing"
errorMessage = ""
error = False

currentTime = 0.0
startTime = 0.0
stop_threads = False

dutyCycleLength = 2.0


# gets the temperature, 
# uses the units from the active schedule if firing, 
# or default units from settings if not firing
def get_current_temperature():
	if status == "firing":
		return io_temp.GetTemp(fire_active.phases['units'])
	else:
		return io_temp.GetTemp(settings.settings['units'])


def get_current_units():
	return fire_active.phases['units']

def get_current_segment():
	return fire_active.currentSegment

def get_current_schedule_name():
	return fire_active.phases['name']

def get_current_status():
	global status
	return status

def get_total_time():
	global currentTime
	return currentTime, fire_active.duration * 3600.0

# returns number of seconds in all of the phases of a firing schedule
# def get_schedule_time():
# 	return fire_active.duration * 3600.0

# sets the kiln in an error state and turns off the relays
def Error(message):
	global error
	global errorMessage
	io_relay.AllOff()
	error = True
	errorMessage = message
	print(message)


# The duty cycle defines what percentage the relays are in the ON or 
# HIGH position allowing electricity to flow through the heating elements

#     +-----------------+           
#     |                 |           
# |   |   DUTY CYCLE    |           
# |                                 
# |---+        +--------+           
# |   |        |        |           
# |   |  LOW   |  HIGH  |           
# |   |        |        |           
# |   +--------+        +-----      
# |                                 
# +---------------------------  

def DutyCycle(percent):
	# min of 100 ms
	print("LOW")
	io_relay.AllOff()
	dutyCycleLowLength = (dutyCycleLength * (1.0 - percent)) / 2.0
	time.sleep(dutyCycleLowLength)

	if io_current.IsConnected():
		Error("Bad Current Sensor or two bad relays, unplug now!")
	time.sleep(dutyCycleLowLength)
	
	print("HIGH")
	io_relay.AllOn()
	dutyCycleHighLength = (dutyCycleLength * percent) / 2.0
	time.sleep(dutyCycleHighLength)
	
	if not io_current.IsConnected():
		Error("Bad Current Sensor, or bad relay")
	time.sleep(dutyCycleHighLength)


# Main loop that sets temperature of kiln based on schedule and current temp
def FireLoop():
	
	global startTime
	global currentTime
	global status
	
	firingComplete = False
	logTime = 0

	# speed used to simulate schedules faster
	speed = 60.0 * 5
	speed = 1.0


	while not firingComplete:

		global stop_threads 
		if stop_threads: 
			print("THREAD STOPPED")
			break

		# sets the current time in seconds
		currentTime = float(time.time() - startTime) * speed

		# gets the current temperature
		currentTemp = fire_active.GetCurrentTemp()

		# gets what the temperature should be at this time in the firing schedule
		targetTemp = fire_active.GetTargetTemp(currentTime / 3600)

		# Needs PID for temperature to define duty cycle
		DutyCycle(0.25)
		
		# Log Temperature
		logTime += 1
		if logTime  > 14:
			logTime = 0
			print("LOGGING " + str(currentTemp) + " " + str(targetTemp))
			fire_logs.AddData(currentTemp, targetTemp)
			# add amp sensor reading to log

		# firing has completed!
		# fire_active.duration
		if currentTime > 35:
			print("FIRING COMPLETE")
			status = "complete"
			firingComplete = True

		# time.sleep(1)


def StartFire(filename):
	global startTime
	global fireThread

	fire_active.StartFire(filename)
	scheduleName = fire_active.phases['name']
	print("Firing: " + scheduleName)

	# Sets up log file for current schedule
	fire_logs.StartLog(scheduleName, fire_active.phases['units'])
	
	status = "firing"
	startTime = time.time()

	# Start a Thread to allow firing sequence to run in the background
	stop_threads = False
	fireThread = threading.Thread(target = FireLoop) 
	fireThread.start() 

def StopFire():
	global fireThread
	global stop_threads
	global status

	stop_threads = True
	try:
		fireThread.join() 
	except NameError:
		print("well, it WASN'T defined after all!")

	# if fireThread.isAlive():
		
	status = "canceled"
	print('thread killed') 




# COST ESTIMATION
# Find the cooldown rate from normal firing
# When the element is on measure the heating rate
# Measure the heating rate based on what temperature it already is
# Create a polynomial from the heating and cooling rates and time