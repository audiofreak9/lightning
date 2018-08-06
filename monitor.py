# -*- coding: utf-8 -*-
#! /usr/bin/env python

"""

monitor.py: A monitoring script for the AS3935 lightning
    sensor on the MOD-1016 v6 breakout board.  Requires both the
    RaspberryPi-AS3935 and RPi.GPIO Python modules.  Note that
    the reset function requires VCT fork of RaspberryPi-AS3935.

simple invocation:
    $ sudo python AS3935-monitor.py

error logging invocation:
    $ sudo python -u AS3935-monitor.py > >(tee -a output.log) 2> >(tee error.log >&2)

Licensed under the GNU General Public License (GPL) version 2 or greater.
Copyright 2014 Vanguard Computer Technology Labs, Inc.

"""

from RPi_AS3935 import RPi_AS3935
import RPi.GPIO as GPIO
import time
from datetime import datetime
GPIO.setmode(GPIO.BCM)
## Rev 1 Raspberry Pi: bus=0
## Rev 2 and later Raspberry Pi: bus=1
## All: address=<i2c add>

sensor = RPi_AS3935(address=0x03, bus=1)

## Uncomment to reset all registers to factory default values.
sensor.reset()

sensor.calibrate(tun_cap=0x0d)
time.sleep(0.002)
sensor.set_indoors(True)
sensor.set_noise_floor
## uncomment/set to filter out false positives
sensor.set_min_strikes(1)

def handle_interrupt(channel):
    time.sleep(0.003)
    global sensor
    reason = sensor.get_interrupt()
    if reason == 0x01:
        print("Noise level too high - adjusting")
        sensor.raise_noise_floor()
    elif reason == 0x04:
        print("Disturber detected - masking")
        sensor.set_mask_disturber(True)
    elif reason == 0x08:
        now = datetime.now()
        ldatetime = now.strftime("%m-%d-%Y") + " at " + now.strftime("%I:%M %p")
        Sdistance = str(sensor.get_distance() * 0.621371)
        Mdistance = str(sensor.get_distance())
        if Mdistance == 1:
            loutput = "Overhead lightning detected - distance = " + Adistance + " mile at %s " % now.strftime("%H:%M:%S.%f")[:-3],now.strftime("%Y-%m-%d")
                        ljson = "[{\"name\":\"Overhead lightning\",\"id\":\"1\",\"dist\":\"" + Mdistance + "\",\"dState\":\" was detected at a distance of " + Mdistance + " km on " + ldatetime + "\",\"dEx\":\"Monkey says \",\"dImg\":\"lightning\"}]"
            print loutput
        elif 40 < Mdistance < 63:
            loutput = "Distant lightning detected - distance = " + Adistance + " miles at %s" % now.strftime("%H:%M:%S.%f")[:-3],now.strftime("%Y-%m-%d")
            ljson = "[{\"name\":\"Distant lightning\",\"id\":\"1\",\"dist\":\"" + Mdistance + "\",\"dState\":\" was detected at a distance of " + Mdistance + " km on " + ldatetime + "\",\"dEx\":\"Monkey says \",\"dImg\":\"lightning\"}]"
            print loutput
        elif 2 <= Mdistance <= 40:
            loutput = "Lightning detected - distance = " + Adistance + " miles at %s" % now.strftime("%H:%M:%S.%f")[:-3],now.strftime("%Y-%m-%d")
            ljson = "[{\"name\":\"Lightning\",\"id\":\"1\",\"dist\":\"" + Mdistance + "\",\"dState\":\" was detected at a distance of " + Mdistance + " km on " + ldatetime + "\",\"dEx\":\"Monkey says \",\"dImg\":\"lightning\"}]"
            print loutput
        else:
            print("Invalid data; distance out of range.")
            ljson = "[{\"name\":\"Lightning\",\"id\":\"1\",\"dist\":\"23\",\"dState\":\" distance was out of range on " + ldatetime + "\",\"dEx\":\"Monkey says \",\"dImg\":\"lightning\"}]"
        f = open('/home/pi/lightning/data.txt','w')
        print >> f, ljson  # or f.write('...\n')
        f.close()

irq_pin = 17
cs_pin = 24
GPIO.setup(irq_pin, GPIO.IN)
GPIO.add_event_detect(irq_pin, GPIO.RISING, callback=handle_interrupt)

def read_settings():
    global min_strikes, noise_floor
    min_strikes = sensor.get_min_strikes()
    noise_floor = sensor.get_noise_floor()

def print_settings():
    print("Minimum allowed strikes is " + str(min_strikes))
    print("Current noise floor is " + str(noise_floor))

running = True

try:
    print("AS3935 Lightning Detection Monitor Script - v0.1")
    print("Monitor proudly built by Tyler and Corey")
    print("Lightning Monitor: ONLINE")
    read_settings()
    print_settings()
    print("")
    while running:
        time.sleep(1.0)

except KeyboardInterrupt:
    print("Lightning Monitor: OFFLINE")
    print("")

finally:
    GPIO.cleanup() # clean up GPIO on CTRL+C exit
