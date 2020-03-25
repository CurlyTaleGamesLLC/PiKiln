# -*- coding: utf-8 -*-

import json
import os
# from datetime import datetime
# import pytz
import time
import threading
import math

from simple_pid import PID

# custom libraries for hardware
import io_relay
import io_temp
import io_current

import fire_logs
import fire_active

import email_notifications

import settings

status = "idle"
errorMessage = ""
error = False

currentTime = 0.0
startTime = 0.0
stop_threads = False
firingComplete = False

# PID Temperature Control
dutyCycleLength = 4.0
pid = PID(1, 0.1, 0.05, setpoint=72)
pid.output_limits = (0, 1)
v = 72
control = 0.0


# gets the temperature, 
# uses the units from the active schedule if firing, 
# or default units from settings if not firing
# truncate the to one decimal place
def get_current_temperature():
	global status
	if status == "firing":
		return math.floor((io_temp.GetTemp(fire_active.phases['units']) * 100)/100.0)
	else:
		return math.floor((io_temp.GetTemp(settings.settings['units']) * 100)/100.0)

def get_current_units():
	global status
	if status == "firing":
		return fire_active.phases['units']
	else:
		return settings.settings['units']
	

def get_current_segment():
	return fire_active.currentSegment

def get_current_schedule_name():
	global status
	if status == "firing":
		return fire_active.phases['name']
	else:
		return ""

def get_current_status():
	global status
	return status

def get_total_time():
	global currentTime
	return currentTime, fire_active.duration * 3600.0

def GetTimeEstimate(filename):
	return fire_active.GetTimeEstimate(filename)


# format time to be hours:mins (2:45)
def FormatTime(value):
    valueMins = value * 60
    if valueMins < 0:
        valueMins = 0
    
    hours = str(int(valueMins // 60))
    mins = str(int(valueMins % 60))

    if len(mins) < 2:
        mins = "0" + mins
    
    return hours + ":" + mins

# puts a hard limit to the max temperature a kiln can go to
def CheckMaxTemp(currentTemp):
	checkTemp = currentTemp

	if fire_active.phases['units'] != settings.settings['units']:
		if fire_active.phases['units'] == "celsius":
			checkTemp = (checkTemp * 1.8) + 32 # convert to F
		else:
			checkTemp = (checkTemp - 32) / 1.8 # convert to C

	if checkTemp > settings.settings['maxTemp']:
		Error("Max Temperature Exceeded")



# returns number of seconds in all of the phases of a firing schedule
# def get_schedule_time():
# 	return fire_active.duration * 3600.0

# sets the kiln in an error state and turns off the relays
def Error(message):
	global error
	global errorMessage
	global firingComplete
	global status
	global stop_threads

	io_relay.AllOff()
	error = True
	errorMessage = message
	firingComplete = True
	stop_threads = True
	if message == "Max Temperature Exceeded":
		emailJSON = {"subject":"Max Temperature Error"}
		email_notifications.SendEmail("max-temp-error.html", emailJSON)
	else:
		emailJSON = {"subject":"Self Check Error"}
		email_notifications.SendEmail("self-check-error.html", emailJSON)

	status = "error"

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
	global dutyCycleLength
	global firingComplete
	# min of 100 ms
	# Off
	print("DUTY = " + str(percent))
	print("LOW")
	dutyCycleLowLength = dutyCycleLength * (1.0 - percent)
	if dutyCycleLowLength > 0.1:
		io_relay.AllOff()
		time.sleep(dutyCycleLowLength / 2)
		if io_current.IsConnected():
			Error("Bad Current Sensor or two bad relays, unplug now!")
			return
		time.sleep(dutyCycleLowLength / 2)
	# On
	print("HIGH")
	dutyCycleHighLength = dutyCycleLength * percent
	if dutyCycleHighLength > 0.1 and not firingComplete:
		io_relay.AllOn()
		time.sleep(dutyCycleHighLength / 2)
		# check for current
		if not io_current.IsConnected():
			Error("Bad Current Sensor, or bad relay")
			return
		time.sleep(dutyCycleHighLength / 2)

	if firingComplete:
		io_relay.AllOff()

# Main loop that sets temperature of kiln based on schedule and current temp
def FireLoop():
	
	global startTime
	global currentTime
	global status
	global stop_threads 
	global v
	global control
	global firingComplete 
	
	firingComplete = False

	# speed used to simulate schedules faster
	speed = 60.0 * 5
	speed = 1.0

	logCounter = 0

	while not firingComplete:
		if stop_threads: 
			io_relay.AllOff()
			print("THREAD STOPPED")
			break

		# sets the current time in seconds
		currentTime = float(time.time() - startTime) * speed

		# gets the current temperature
		currentTemp = fire_active.GetCurrentTemp()
		
		# check to see if the max temp has been exceeded
		CheckMaxTemp(currentTemp)

		# gets what the temperature should be at this time in the firing schedule
		targetTemp = fire_active.GetTargetTemp(currentTime / 3600)
		print("Target Temp = " + str(targetTemp) + ", " + str(currentTemp))

		# compute new ouput from the PID according to the systems current value
		pid.setpoint = targetTemp
		control = pid(v)
		DutyCycle(control)

		# feed the PID output to the system and get its current value
		v = currentTemp

		print("pid test")
		print(v)
		print(control)
		

		# Log Temperature every 5 duty cycles
		logCounter += 1
		if logCounter > 5:
			logCounter = 0
			print("LOGGING " + str(currentTemp) + " " + str(targetTemp))
			fire_logs.AddData(currentTemp, targetTemp)
			# add amp sensor reading to log

		# firing has completed!
		# fire_active.duration
		print("duration = " + str(currentTime) + " / " + str(fire_active.duration * 3600))
		if currentTime > fire_active.duration * 3600:
			print("FIRING COMPLETE")
			status = "complete"

			emailJSON = {
				"subject":fire_active.phases['name'] + " - Firing Complete!", 
				"schedule":fire_active.phases['name'], 
				"duration":FormatTime(fire_active.duration), 
				"cost":"$3.50"
			}
			email_notifications.SendEmail("complete.html", emailJSON)

			firingComplete = True
			io_relay.AllOff()


def StartFire(filename):
	global startTime
	global fireThread
	global stop_threads
	global status

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
	# return '{"result":true}'

def StopFire():
	global fireThread
	global stop_threads
	global status

	io_relay.AllOff()

	stop_threads = True
	try:
		fireThread.join() 
	except NameError:
		print("thread wasn't defined")

	# if fireThread.isAlive():
		
	status = "canceled"
	print('thread killed') 




# COST ESTIMATION
# Find the cooldown rate from normal firing
# When the element is on measure the heating rate
# Measure the heating rate based on what temperature it already is
# Create a polynomial from the heating and cooling rates and time