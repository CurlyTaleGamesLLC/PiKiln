import board
import busio
import digitalio
import adafruit_max31856

import settings

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D6)

max31856 = adafruit_max31856.MAX31856(spi, cs)

# isCelcius = False
# offset = 0

def GetTemp(units):
	tempC = max31856.temperature
	# tempF = tempC * 9 / 5 + 32
	tempF = (tempC * 1.8) + 32

	# convert offset to correct units
	offset = settings.settings['offsetTemp']
	if units != settings.settings['units']:
		if units == "celsius":
			offset = (offset - 32) / 1.8
		else:
			offset = (offset * 1.8) + 32

	# return the temp + the offset
	if units == "celsius":
		return tempC + offset
	else:
		return tempF + offset

# print(str(GetTemp("celsius", 0)))