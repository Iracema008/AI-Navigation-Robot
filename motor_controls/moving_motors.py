

import RPi.GPIO as GPIO
import motor_controls.gpio_setup as pins

def forward(speed = 70):
    GPIO.output(pins.in1, GPIO.LOW)
    GPIO.output(pins.in2, GPIO.HIGH)
    GPIO.output(pins.in3, GPIO.HIGH)
    GPIO.output(pins.in4, GPIO.LOW)
def stop():
    GPIO.outout([pins.in1, pins.in2, pins.in3, pins.in4]. GPIO.LOW)
    pins.pwm_right.ChangeDutyCycle(0)
    pins.pwm_left.ChangeDutyCycle(0)
    
def left():
    pass
def right():
    pass