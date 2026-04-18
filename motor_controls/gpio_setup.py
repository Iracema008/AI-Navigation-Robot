"Motor setup while ONLY connected to Raspberry PI"

import RPi.GPIO as GPIO
import time

# TODO: Double check inputs (we ended up switching out in1/2 to left motor)
# Left motor control inputs
in1 = 24
in2 = 23
ena = 25

# Right motor control inputs
in3 = 16
in4 = 27
enb = 22

# line sensor
line_ir = 17

pwm_right = None
pwm_left = None

def layout_gpio():
    global pwm_right, pwm_left
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # pi sends OUT electrical signal to l298n
    GPIO.setup(in1, GPIO.OUT)
    GPIO.setup(in2, GPIO.OUT)
    GPIO.setup(ena, GPIO.OUT)
    GPIO.setup(in3, GPIO.OUT)
    GPIO.setup(in4, GPIO.OUT)
    GPIO.setup(enb, GPIO.OUT)
    
    # pi recieves sensor INPUT from ir
    GPIO.setup(line_ir, GPIO.IN)

    # our speed, in hz
    pwm_right = GPIO.PWM(ena, 1000)
    pwm_left = GPIO.PWM(enb, 1000)

    pwm_right.start(0)
    pwm_left.start(0)

def kill_cycle():
    if pwm_right:
        pwm_right.stop()
    if pwm_left:
        pwm_left.stop()

    GPIO.cleanup()