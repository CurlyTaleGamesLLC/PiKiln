import RPi.GPIO as GPIO
import time

ledpin = 12
ledpin2 = 16

GPIO.setmode(GPIO.BCM)

GPIO.setup(ledpin, GPIO.OUT)
GPIO.output(ledpin, GPIO.HIGH)

GPIO.setup(ledpin2, GPIO.OUT)
GPIO.output(ledpin2, GPIO.HIGH)


time.sleep(10)

GPIO.output(ledpin, GPIO.LOW)
GPIO.output(ledpin2, GPIO.LOW)

GPIO.cleanup()
