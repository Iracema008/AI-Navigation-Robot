''' Ultrasonic sensor detection '''

import RPi.GPIO as GPIO
import time

#actual pins on sensor, trig = 31, echo = 29
# shoud be in notebook
TRIG = 6
ECHO = 5 

STOP_DISTANCE = 20

def setup_ultrasonic():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.1)

def get_distance():
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)

    timeout = time.time() + 0.1
    while GPIO.input(ECHO) == 0:
        if time.time() > timeout:
            return 999
    pulse_start = time.time()

    timeout = time.time() + 0.1
    while GPIO.input(ECHO) == 1:
        if time.time() > timeout:
            return 999
    pulse_end = time.time()

    duration = pulse_end - pulse_start
    distance = (duration * 34300) / 2
    return round(distance, 1)

def obstacle_detected():
    return get_distance() < STOP_DISTANCE
