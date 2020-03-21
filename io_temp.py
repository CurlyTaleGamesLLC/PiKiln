import board
import busio
import digitalio
import adafruit_max31856

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D6)

max31856 = adafruit_max31856.MAX31856(spi, cs)

# isCelcius = False
# offset = 0

def GetTemp(units, offset):
	tempC = max31856.temperature
	tempF = tempC * 9 / 5 + 32
	if units == "celsius":
		return tempC + offset
	else:
		return tempF + offset

# print(str(GetTemp("celsius", 0)))