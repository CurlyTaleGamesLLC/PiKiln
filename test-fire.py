import time

import io_relay
import io_temp
import io_current

def TestSensors():
	print("Reset Current Sensor")
	io_current.Reset()

	print("Relays on")
	io_relay.SetState(0,True)
	io_relay.SetState(1,True)

	i = 0
	while i < 10:
		i += 1
		print("")
		print(str(io_temp.GetTemp()))
		print(str(io_current.GetVoltage()))
		print(str(io_current.IsConnected()))
		time.sleep(3)

	print("Relays off")
	print(str(io_temp.GetTemp()))
	io_relay.SetState(0,False)
	io_relay.SetState(1,False)

	time.sleep(1)
	print(str(io_current.GetVoltage()))
	print(str(io_current.IsConnected()))

def RelaySelfTest():
	# Test both relays off
	io_relay.AllOff()
	time.sleep(0.5)
	if io_current.IsConnected():
		return "ERROR: Electricity Detected when both relays are off, unplug now! Possible faulty relays or current sensor"
	time.sleep(0.5)

	# Test Relay 1
	io_relay.SetState(0,False)
	io_relay.SetState(1,True)
	time.sleep(0.5)
	if io_current.IsConnected():
		io_relay.AllOff()
		return "ERROR: Relay 1 is Bad, replace Relay 1"
	time.sleep(0.5)

	# Test Relay 2
	io_relay.SetState(0,True)
	io_relay.SetState(1,False)
	time.sleep(0.5)
	if io_current.IsConnected():
		return "ERROR: Relay 2 is Bad, replace Relay 2"
	time.sleep(0.5)

	# Test Current Sensor
	io_relay.AllOn()
	time.sleep(0.5)
	if io_current.IsConnected():
		io_relay.AllOff()
		return "Relay Self Test Success"
	
	io_relay.AllOff()
	return "Error: Current Sensor Failed to detect current"


print(RelaySelfTest())

