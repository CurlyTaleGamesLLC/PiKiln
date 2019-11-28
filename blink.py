import RPi.GPIO as GPIO
import time

ledpin = 4

GPIO.setmode(GPIO.BCM)

GPIO.setup(ledpin, GPIO.OUT)
GPIO.output(ledpin, GPIO.HIGH)

time.sleep(3)

GPIO.output(ledpin, GPIO.LOW)
GPIO.cleanup()