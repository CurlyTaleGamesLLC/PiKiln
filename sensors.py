# -*- coding: utf-8 -*-

from flask import Flask, jsonify
import time
import json
import os

# GPIO libraries
import board
import busio

# libraries for temperature sensor
import digitalio
import adafruit_max31856

# create a spi object
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

# allocate a CS pin and set the direction
cs = digitalio.DigitalInOut(board.D5)
cs.direction = digitalio.Direction.OUTPUT

# create a thermocouple object with the above
thermocouple = adafruit_max31856.MAX31856(spi, cs)

# ADS1115 library (analog to digital converter) for Current Sensor
# import adafruit_ads1x15.ads1015 as ADS
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# create a i2c object
i2c = busio.I2C(board.SCL, board.SDA)



dutyCycleLength = 1.0

def get_temperature(isCelsius):

    # print the temperature!
    print(thermocouple.temperature)

    temperature = 0
    if isCelsius:
        print("temp celsius")
    else:
        print("temp fehrinheit")
    return temperature

def get_current():
    current = 0

    # ads = ADS.ADS1015(i2c)
    ads = ADS.ADS1115(i2c)
    # ads.gain = 16

    chan = AnalogIn(ads, ADS.P0)
    print(chan.value, chan.voltage)

    return current

def self_check():
    if check_relay(1):
        return jsonify(relay=1)
    if check_relay(2):
        return jsonify(relay=2)
    return jsonify(relay=0)

def check_relay(relayNumber):
    print("checking relay" + relayNumber)
    isBadRelay = False
    
    duty_cycle(relayNumber, 0.0)
    time.sleep(0.5)
    if get_current > 0:
        isBadRelay = True

    duty_cycle(relayNumber, 1.0)
    time.sleep(0.5)
    if get_current == 0:
        isBadRelay = True

    if isBadRelay:
        print("Relay " + relayNumber + " is bad")
    return isBadRelay

def duty_cycle(relayNumber, percent):
    # min of 100 ms
    print("LOW")
    set_relays(relayNumber, False)
    time.sleep(dutyCycleLength * (1.0 - percent))
    
    print("HIGH")
    set_relays(relayNumber, True)
    time.sleep(dutyCycleLength * percent)

def set_relays(relayNumber, state):
    if relayNumber == 0:
        print("BOTH RELAYS")
    if relayNumber == 1:
        print("RELAY 1")
    if relayNumber == 2:
        print("RELAY 2")