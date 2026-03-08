"Motor setup while ONLY connected to Raspberry PI"

import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# These numbers are our physical wire connections
# Left motor control inputs
in1 = 24
in2 = 23
ena = 25

# Right motor control inputs
in3 = 17
in4 = 27
enb = 22


GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(ena, GPIO.OUT)

GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)
GPIO.setup(enb, GPIO.OUT)

pwm_a = GPIO.PWM(ena, 1000)
pwm_b = GPIO.PWM(enb, 1000)

def forward():
    pass
def back():
    pass
def left():
    pass
def right():
    pass