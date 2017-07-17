#!/usr/bin/env python2.7
#parkingLights.py
import threading, logging, time, signal
from blinkt import set_pixel, set_brightness, show, clear
import colorsys
#import RPi.GPIO as GPIO
import pigpio

def gpioSetup():
    #setup GPIO
    global GPIO, GPIO_TRIG, GPIO_ECHO
    GPIO = pigpio.pi()
    #GPIO.setmode(GPIO.BCM)
    GPIO_TRIG = 22
    GPIO_ECHO = 25

    GPIO.set_mode(GPIO_TRIG, pigpio.OUTPUT)
    GPIO.set_mode(GPIO_ECHO, pigpio.INPUT)

def colors():
    global distance, speed
    speed = 0.05
    distance = 0
    while True:
        for i in range(7,0,-1):
            #print distance
            if distance > 600: # max response time
                #print 'door open'
                h = 0.6
                speed = 0.5
            elif 300 < distance < 600: # entering garage - green
                #print 'green'
                h = 0.33
                speed = 0.1
            elif 150 < distance < 300: # change to yellow at 250
                #print 'yellow'
                h = 0.17
                speed = 0.2
            elif distance < 150: # change to red at 100
                #print 'red'
                h = 0.0
                speed = 0.5
            else: # unknown
                #print 'fail'
                h = 0.85
            clear()
            y = 1.0
            for x in range(0,5):
                r,g,b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, 1, y)]
                set_pixel((i+x)%8, r, g, b)
                y = y *0.55
            show()
            time.sleep(speed)

def cbfStart(gpio, level, tick):
    global startTick
    startTick = tick
    #print startTick

def cbfEnd(gpio, level, tick):
    global endTick, startTick, distance
    endTick = tick

    ticksElapsed = pigpio.tickDiff(startTick, endTick)
    if ticksElapsed > 10:
        distance = ticksElapsed / 58
        #print "d = %s " % distance
    #else:
        #print ticksElapsed
    #print endTick

def measure():
    global GPIO_TRIG, GPIO_ECHO, GPIO, startTick, endTick, distance

    startEcho = GPIO.callback(GPIO_ECHO, pigpio.RISING_EDGE, cbfStart)
    endEcho = GPIO.callback(GPIO_ECHO, pigpio.FALLING_EDGE, cbfEnd)
    startTick = GPIO.get_current_tick()
    endTick = startTick

    while True:
        GPIO.gpio_trigger(GPIO_TRIG, 12, 1)
        #time.sleep(0.005)
        #if GPIO.wait_for_edge(GPIO_ECHO, pigpio.FALLING_EDGE, 0.200): #was .3
        #    ticksElapsed = pigpio.tickDiff(startTick, endTick)
        #    print ticksElapsed
        #    measurement = ticksElapsed / 58
        #    distance = measurement
        #else:
        #        print "missed falling edge"
                # distance = 0
        #else: #didn't catch start of echo, abort
        # distance = 0 (changed to just not update it)
        #print distance
        time.sleep(0.2) #was .3

if __name__ == '__main__':
    global GPIO
    try:
        gpioSetup()
        t = threading.Thread(target=colors)
        t.setDaemon(True)
        t.start()
        measure()
        while True:
            signal.pause()

    except KeyboardInterrupt:
        print "Measurement stopped by User"
        GPIO.stop()

