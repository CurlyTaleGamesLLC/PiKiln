import time
import board
import busio
#import adafruit_ads1x15.ads1015 as ADS
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import RPi.GPIO as GPIO

ledpin = 12
ledpin2 = 16

GPIO.setmode(GPIO.BCM)

GPIO.setup(ledpin, GPIO.OUT)
GPIO.setup(ledpin2, GPIO.OUT)


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

print("{:>5}\t{:>5}".format('raw', 'v'))

counter = 20

while True:
	ads.gain = gains[1]
	print("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))
	counter = counter - 1
	if counter > 0:
		GPIO.output(ledpin, GPIO.HIGH)
		GPIO.output(ledpin2, GPIO.HIGH)
	else:
		GPIO.output(ledpin, GPIO.LOW)
		GPIO.output(ledpin2, GPIO.LOW)
	time.sleep(0.5)

GPIO.cleanup()
