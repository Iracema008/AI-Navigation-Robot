'''Line Sensor Readings'''

import RPi.GPIO as GPIO
import time
import motor_controls.gpio_setup as pins




def detect_line():
    return GPIO.input(pins.line_ir) == GPIO.LOW


