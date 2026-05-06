''' Working line following test, w/ultra sonic. '''

import RPi.GPIO as GPIO
import time

from motor_controls.gpio_setup import layout_gpio, kill_cycle
from motor_controls.moving_motors import forward, left, right, stop
from sensors.hcsr04 import setup_ultrasonic, get_distance, obstacle_detected, STOP_DISTANCE

FORWARD_SPEED = 70 
TURN_SPEED = 70
RECOVER_SPEED = 70
LOOP_DELAY= 0.02
MAX_OFF = 15
RECOVER_TIME = 0.5
OBBY_CHECK = 0.1

LINE_IR = 17

def detect_line():
    return GPIO.input(LINE_IR) == GPIO.HIGH

def wait_path():
    print("Wait for warehouse path to clear")
    stop()
    while True:
        d = get_distance()
        if d >= STOP_DISTANCE:
            print("Cleared")
            return
        else:
            # add th e reroute later
            pass
        print("Still blocked")
        time.sleep(0.3)
    
def recover_line(last_seen):
    print("Searching for line ")
    stop()
    time.sleep(0.1)

    for attempt in range(1,  6):
        sweep_time = RECOVER_TIME * attempt

        # Start from where we left off
        start = time.time()
        while time.time() - start < sweep_time:
            if detect_line():
                print(f"  Line found on attempt {attempt}!")
                return True

            if last_seen == "right":
                right(RECOVER_SPEED)
            else:
                left(RECOVER_SPEED)
            time.sleep(0.02)
        stop()
        time.sleep(0.1)

        # try turning to other side 
        start = time.time()

        while time.time() - start < sweep_time * 2:
            if detect_line():
                print(f"  Line found on attempt {attempt}!")
                return True
            if last_seen == "right":
                left(RECOVER_SPEED)
            else:
                right(RECOVER_SPEED)
            time.sleep(0.02)
        stop()
        time.sleep(0.1)

    print(" ouldnt find line")
    return False



def main():
    layout_gpio()
    
    setup_ultrasonic()
    GPIO.setup(LINE_IR, GPIO.IN)


    print("Started, place Nodey on line.\nNodey will stop if warehouse path is blocked")
    print("Ctrl+C to stop.\n")
    time.sleep(2)

    last_seen = "right"
    # maybe switch higher? 
    speed = 50
    off_count = 0
    last_obstacle_check = time.time()


    try:
        while True:
            if time.time() - last_obstacle_check >= OBBY_CHECK:
                last_obstacle_check = time.time()
                if obstacle_detected():
                    wait_path()
                    speed =50
                    off_count = 0
        
            if detect_line():
                speed = min(speed + 1, FORWARD_SPEED)
                forward(speed)
                if off_count == 0:
                    last_seen = "center"
                off_count = 0

            # if not, check other ways
            else:
                speed = 50
                off_count += 1

                if last_seen == "left":
                    left(TURN_SPEED)
                    last_seen = "left"

                elif last_seen == "right":
                    right(TURN_SPEED)
                    last_seen = "right"

                # just stick to right for now,
                else:
                    right(TURN_SPEED)
                    last_seen = "right"

                # if too many errors, stop Nodey
                if off_count >= MAX_OFF:
                    off_count = 0
                    found = recover_line(last_seen)
                    if not found:
                        print("Unable to get back on Path")
                        break

            time.sleep(LOOP_DELAY)

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        stop()
        kill_cycle()

if __name__ == "__main__":
    main()


