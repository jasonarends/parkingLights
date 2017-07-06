#!/usr/bin/env python2.7
#parkingLights.py
import threading, logging, time
from blinkt import set_pixel, set_brightness, show, clear
import colorsys
import RPi.GPIO as GPIO

def gpioSetup():
    #setup GPIO
    global GPIO_TRIG, GPIO_ECHO
    GPIO.setmode(GPIO.BCM)
    GPIO_TRIG = 22
    GPIO_ECHO = 25

    GPIO.setup(GPIO_TRIG, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)

def colors():
    global distance, speed
    speed = 0.05
    while True:
        for i in range(7,0,-1):
            #print distance
            if distance > 2800: # max response time
                #print 'door open'
                h = 0.6
                speed = 0.5
            elif 450 < distance < 2800: # entering garage - green
                #print 'green'
                h = 0.33
                speed = 0.1
            elif 150 < distance < 450: # change to yellow at 250
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

def measure():
    global GPIO_TRIG, GPIO_ECHO
    
    # set trigger to high
    GPIO.output(GPIO_TRIG, True)

    # set trigger to low after 0.01ms
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIG, False)

    startTime = time.time()
    
    GPIO.wait_for_edge(GPIO_ECHO, GPIO_RISING, timeout=1000)
    stopTime = time.time()

    timeElapsed = stopTime - startTime
    measurement = (timeElapsed * 34300) / 2

    return measurement

if __name__ == '__main__':
    global distance
    try:
        t = threading.Thread(target=colors)
        t.setDaemon(True)
        t.start()
        while True:
            distance = measure()
            print distance
            time.sleep(0.6)

    except KeyboardInterrupt:
        print "Measurement stopped by User"
        GPIO.cleanup()

