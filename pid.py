from simple_pid import PID

import time

import settings

import io_temp
import io_relay

print(settings.load_settings())

pid = PID(1, 0.1, 0.05, setpoint=1)
pid.output_limits = (0, 1)

# assume we have a system we want to control in controlled_system
# v = controlled_system.update(0)
# v = io_temp.GetTemp("fahrenheit")
v = io_temp.GetTemp("fahrenheit")
print("pid test")
print(v)
pid.setpoint = 79

io_relay.AllOff()
time.sleep(3)

dutyCycleLength = 4

control = 0.0

def DutyCycle(percent):
	global dutyCycleLength
	# min of 100 ms
	# Off
	print("DUTY = " + str(percent))
	print("LOW")
	dutyCycleLowLength = dutyCycleLength * (1.0 - percent)
	if dutyCycleLowLength > 0.1:
		io_relay.AllOff()
		time.sleep(dutyCycleLowLength)
	# On
	print("HIGH")
	dutyCycleHighLength = dutyCycleLength * percent
	if dutyCycleHighLength > 0.1:
		io_relay.AllOn()
		time.sleep(dutyCycleHighLength)


while True:
	# compute new ouput from the PID according to the systems current value
	control = pid(v)
	DutyCycle(control)

	# feed the PID output to the system and get its current value
	# v = controlled_system.update(control)
	v = io_temp.GetTemp("fahrenheit")

	print("pid test")
	print(v)
	print(control)