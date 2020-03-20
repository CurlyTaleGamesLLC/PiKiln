import RPi.GPIO as GPIO

relays = [12,16]

GPIO.setmode(GPIO.BCM)

for relay in relays:
    GPIO.setup(relay, GPIO.OUT)

def SetState(index, isOn):
    if isOn:
        GPIO.output(relays[index], GPIO.HIGH)
    else:
        GPIO.output(relays[index], GPIO.LOW)


# GPIO.cleanup()
