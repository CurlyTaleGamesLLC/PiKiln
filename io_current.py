# import time
import board
import busio
#import adafruit_ads1x15.ads1015 as ADS
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
#ads = ADS.ADS1015(i2c)
ads = ADS.ADS1115(i2c)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)

# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)
gains = (2/3, 1, 2, 4, 8, 16)
ads.gain = gains[1]

referenceVoltage = 1.649
threshold = 0.1

def GetVoltage():
	return abs(float(chan.voltage) - referenceVoltage)

def Reset():
	referenceVoltage = chan.voltage

def IsConnected():
	if GetVoltage() > threshold:
		return True
	else:
		return False

# print(str(GetVoltage()))
# print(str(IsConnected()))