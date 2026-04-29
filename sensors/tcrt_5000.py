'''Line Sensor Readings'''

import RPi.GPIO as GPIO
import time
import motor_controls.gpio_setup as pins

from motor_controls.moving_motors import forward, right




def detect_line():
    return GPIO.input(pins.line_ir) == GPIO.LOW


def wait_at_intersection(segment_time=2.0):
    start = time.time()
    while time.time() - start < segment_time:
        if detect_line():
            forward(70)
        else:
            right(70, 35)
        time.sleep(0.05)