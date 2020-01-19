# -*- coding: utf-8 -*-

from flask import Flask, jsonify
import time
import json
import os

dutyCycleLength = 1.0

def get_temperature(isCelsius):
    temperature = 0
    if isCelsius:
        print("temp celsius")
    else:
        print("temp fehrinheit")
    return temperature

def get_current():
    current = 0
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