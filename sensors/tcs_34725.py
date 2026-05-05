"""RGB Sensor Readings """
import adafruit_tcs34725
import board
import time

i2c = board.I2C()
rgb_sensor = adafruit_tcs34725.TCS34725(i2c)

def classify_color(r, g, b):
    if r > 150 and g < 100 and b < 100:
        return "red"
    elif r > 150 and g > 80 and g < 160 and b < 80:
        return "orange"
    elif g > 150 and r < 100 and b < 100:
        return "green"
    elif b > 150 and r < 100 and g < 100:
        return "blue"
    elif r > 150 and g > 150 and b < 100:
        return "yellow"
    else:
        return None

def detect_color():
    r, g, b = rgb_sensor.color_rgb_bytes
    return classify_color(r, g, b)

def read_rgb():
    while True:
        r, g, b = rgb_sensor.color_rgb_bytes
        color = classify_color(r, g, b)
        print(f"RGB Color: ({r}, {g}, {b}) -> {color or 'unknown'}")
        time.sleep(1)