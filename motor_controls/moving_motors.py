''' Motor controls '''

import RPi.GPIO as GPIO
import motor_controls.gpio_setup as pins


def forward():
    GPIO.output(pins.in1, GPIO.HIGH)
    GPIO.output(pins.in2, GPIO.LOW)
    GPIO.output(pins.in3, GPIO.HIGH)
    GPIO.output(pins.in4, GPIO.LOW)

    pins.pwm_right.ChangeDutyCycle(0)
    pins.pwm_left.ChangeDutyCycle(0)

# these are the same
def left(fast=70, slow=35):
    GPIO.output(pins.in1, GPIO.HIGH)
    GPIO.output(pins.in2, GPIO.LOW)
    GPIO.output(pins.in3, GPIO.LOW)
    GPIO.output(pins.in4, GPIO.HIGH)
    pins.pwm_right.ChangeDutyCycle(fast)
    pins.pwm_left.ChangeDutyCycle(slow)

def right(fast=70, slow=35):
    GPIO.output(pins.in1, GPIO.LOW)
    GPIO.output(pins.in2, GPIO.HIGH)
    GPIO.output(pins.in3, GPIO.HIGH)
    GPIO.output(pins.in4, GPIO.LOW)
    pins.pwm_right.ChangeDutyCycle(slow)
    pins.pwm_left.ChangeDutyCycle(fast)

def stop():
    GPIO.output([pins.in1, pins.in2, pins.in3, pins.in4], GPIO.LOW)
    pins.pwm_right.ChangeDutyCycle(0)
    pins.pwm_left.ChangeDutyCycle(0)
