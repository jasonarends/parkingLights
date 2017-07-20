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
    global distance
    distance = 0
    
    while True:
        while distance > 800: #testing with max response 800 since i know it usually shows >2000 when empty
            for i in range(7,0,-1):
                clear()
                y = 1.0
                for x in range(0,3):
                    r,g,b = [int(c * 255) for c in colorsys.hsv_to_rgb(0.6, 1, y)] #slow purple 3 dots
                    set_pixel((i+x)%8, r, g, b)
                    y = y *0.5
                show()
                time.sleep(0.4)
                
        while 400 < distance < 800: #entering garage - green fast 4 dots
            for i in range(7,0,-1):
                clear()
                y = 1.0
                for x in range(0,4):
                    r,g,b = [int(c * 255) for c in colorsys.hsv_to_rgb(0.33, 1, y)]
                    set_pixel((i+x)%8, r, g, b)
                    y = y *0.5
                show()
                time.sleep(0.1)
                
        while 140 < distance < 400: #entering garage - yellow slower 5 dots
            for i in range(7,0,-1):
                clear()
                y = 1.0
                for x in range(0,5):
                    r,g,b = [int(c * 255) for c in colorsys.hsv_to_rgb(0.16, 1, y)]
                    set_pixel((i+x)%8, r, g, b)
                    y = y *0.55
                show()
                time.sleep(0.2)

        while 120 < distance < 140: #entering garage - within range, red slow 6 dots
            for i in range(14,0,-1):
                j = int(i/2)
                clear()
                y = 1.0
                for x in range(0,6):
                    r,g,b = [int(c * 255) for c in colorsys.hsv_to_rgb(0.0, 1, y)]
                    set_pixel((j+x)%8, r, g, b)
                    y = y *0.5
                show()
                time.sleep(0.25) #updates faster than .5 and changed range to 0-14 but divides it by 2 so only moves half as fast as it updates
        
        while 105 < distance < 120: #entering garage - red, stopped
            for x in range(0,7):
                set_pixel(x, 255, 0, 0)
            show()
            time.sleep(0.1)
            
        while distance < 105: #entering garage - green fast 4 dots
            for i in range(7,0,1):
                clear()
                y = 1.0
                for x in range(0,6):
                    r,g,b = [int(c * 255) for c in colorsys.hsv_to_rgb(0.33, 1, y)]
                    set_pixel((i-x)%8, r, g, b)
                    y = y *0.5
                show()
                time.sleep(0.1)

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

