import board
import busio
import digitalio
import adafruit_max31856

import settings

import time

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

cs = [digitalio.DigitalInOut(board.D5), digitalio.DigitalInOut(board.D6)]
# , digitalio.DigitalInOut(board.D13)
max31856 = []

for i in range(len(cs)):
	max31856.append(adafruit_max31856.MAX31856(spi, cs[i]))

# max31856 = adafruit_max31856.MAX31856(spi, cs)

def GetTemp(units, index):
	tempC = max31856[index].temperature
	tempF = (tempC * 1.8) + 32

	# convert offset to correct units
	offset = 0
	# offset = settings.settings['offsetTemp']
	# if units != settings.settings['units']:
	# 	if units == "celsius":
	# 		offset = offset / 1.8
	# 	else:
	# 		offset = offset * 1.8

	# return the temp + the offset
	if units == "celsius":
		return tempC + offset
	else:
		return tempF + offset

while True:
	print("INDEX 0 = " + str(GetTemp("fahrenheit", 0)))
	time.sleep(1)
	print("INDEX 1 = " + str(GetTemp("fahrenheit", 1)))
	time.sleep(1)
	print("")
	time.sleep(1)
