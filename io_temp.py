import board
import busio
import digitalio
import adafruit_max31856

import settings

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# cs = digitalio.DigitalInOut(board.D6)
# max31856 = adafruit_max31856.MAX31856(spi, cs)

cs = [digitalio.DigitalInOut(board.D6), digitalio.DigitalInOut(board.D6), digitalio.DigitalInOut(board.D6)]
max31856 = []

for i in range(len(cs)):
	max31856.append(adafruit_max31856.MAX31856(spi, cs[i]))

def GetTemp(units):
	return GetTempIndex(units, 0)

def GetAllTemp(units):
	tempReadings = []
	averageReading = 0
	for i in range(settings.settings['tempCount']):
		newReading = GetTempIndex(units, i)
		tempReadings.append(newReading)
		averageReading += newReading

	averageReading = averageReading / settings.settings['tempCount']
	tempReadings.append(averageReading)

	return tempReadings


def GetTempIndex(units, index):
	tempC = max31856[index].temperature
	tempF = (tempC * 1.8) + 32

	# convert offset to correct units
	offset = settings.settings['tempOffsets'][index]
	if units != settings.settings['units']:
		if units == "celsius":
			offset = offset / 1.8
		else:
			offset = offset * 1.8

	# return the temp + the offset
	if units == "celsius":
		return tempC + offset
	else:
		return tempF + offset

# print(str(GetTemp("celsius", 0)))