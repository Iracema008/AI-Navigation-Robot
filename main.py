''' Run main logic '''

import time
import RPi.GPIO as GPIO

from motor_controls.moving_motors import forward, left, right, stop
from motor_controls.gpio_setup import layout_gpio, kill_cycle
from sensors.tcrt_5000 import detect_line
from sensors.tcs_34725 import detect_color
from navigation.grid import pickup_nodes
from navigation.sa_optimizer import simulated_annealing
from navigation.astar import astar

# change segement based on tests
SEGMENT_TIME = 2.0
TURN_DURATION = 0.4

# hard coded turn map for testing, coming_from, at_junction, going_to -> direction
# Fill this in later to match physical track
TURN_MAP = {
    # start
    ("start", "node1", "node3"):"straight",
    ("start", "node1", "node4"): "right",
    ("start", "node2", "node4"): "left",
    ("start", "node2", "node5"): "straight",
    # node 1
    ("node1", "node3", "node6"): "straight",
    ("node1", "node3", "node7"): "right",
    ("node1", "node4", "node2"): "right",
    ("node1", "node4", "node7"): "straight",
    # node 2
    ("node2", "node4", "node1"): "right",
    ("node2", "node4", "node7"): "straight",
    ("node2", "node5", "node7"): "right",
    # node3 
    ("node3", "node6", "end"): "right",
    ("node3", "node7", "node4"): "left",
    ("node3", "node7", "end"): "right",
    # node4
    ("node4", "node7", "node3"): "left",
    ("node4", "node7", "end"): "straight",
    ("node4", "node2", "start"): "right",
    ("node4", "node2", "node5"): "left",
    # node5
    ("node5", "node2", "start"): "right",
    ("node5", "node2", "node4"): "left",
    ("node5", "node7", "node4"): "left",
    ("node5", "node7", "end"): "right",

    ("node6", "end", "node7"): "left",
    ("node6", "node3", "node1"): "straight",
    ("node6", "node3", "node7"): "left",
    
    ("node7", "end", "node6"): "right",
    ("node7", "node3", "node1"): "right",
    ("node7", "node3", "node6"): "left",
    ("node7", "node4", "node2"): "right",
    ("node7", "node4", "node1"): "left",
    ("node7", "node5", "node2"): "right",
    # end
    ("end", "node6", "node3"): "right",
    ("end", "node7", "node4"): "right",
    ("end", "node7", "node3"): "left",
}
detected_pickups = []

def determine_turn(prev_node, curr_node, next_node):
    return TURN_MAP.get((prev_node, curr_node, next_node), "straight")

# try to keep speed at 70, else doesn't turn well.
def execute_turn(direction):
    stop()
    time.sleep(0.1)
    if direction == "left":
        left(fast=70, slow=0)
    elif direction == "right":
        right(fast=70, slow=0)
    else:
        forward(70)
    time.sleep(TURN_DURATION)
    stop()
    time.sleep(0.1)
    
last_seen = "right"

'''def follow_line():
    global last_seen
    start_time = time.time()
    while time.time() - start_time < SEGMENT_TIME:
        if detect_line():
            # On the black line, go straight
            forward(50)
            last_seen = "center"
        else:
            # Lost the line ? sweep back the way we came from
            if last_seen != "center":
                # Already know which way to recover
                if last_seen == "right":
                    right(60, 0)
                else:
                    left(60, 0)
            else:
                # Just lost it from center, default sweep right
                right(60, 0)
                last_seen = "right"
        time.sleep(0.03)
    stop()'''
def follow_line_until_color(timeout=10):
    """New Follow line function to follow until color sensor detects tape or timeout"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        # check for colored tape (arrived at a node)
        color = detect_color()
        if color is not None:
            stop()
            return color

        # otherwise keep following the black line
        if detect_line():
            forward(50)
        else:
            right(60, 0)
        time.sleep(0.03)

    stop()
    return None
    
def check_pickup():
    color = detect_color()
    if color is None:
        return
    expected_colors = list(pickup_nodes.values())

    if color in expected_colors and color not in detected_pickups:
        detected_pickups.append(color)
        node = [n for n, c in pickup_nodes.items() if c == color][0]
    
        print(f"Pickup point detected: {color} at {node} ({len(detected_pickups)}/{len(expected_colors)})")
    elif color in detected_pickups:
        print(f"Already collected: {color}, continuing...")
    else:
        print(f"Unexpected color: {color}, continuing...")

'''def navigate_path(path):
    print(f"  Navigating: {path}")
    for i in range(len(path) - 1):
        current = path[i]
        next_node = path[i + 1]
        prev_node = path[i - 1] if i > 0 else None
        if prev_node:
            direction = determine_turn(prev_node, current, next_node)
            execute_turn(direction)
        follow_line()
        check_pickup()
        print(f"  Reached: {next_node}")
    stop()'''


def navigate_path(path):
    print(f"  Navigating: {path}")
    for i in range(len(path) - 1):
        current = path[i]
        next_node = path[i + 1]
        prev_node = path[i - 1] if i > 0 else None

        if prev_node:
            direction = determine_turn(prev_node, current, next_node)
            execute_turn(direction)

        color = follow_line_until_color()

        if color:
            print(f"  Reached: {next_node}")
        else:
            print(f"  Warning: timeout reaching {next_node}")

        if next_node in pickup_nodes:
            detected_pickups.append(next_node)
            print(f"  Pickup detected at {next_node} ({len(detected_pickups)}/{len(pickup_nodes)})")
            stop()
            time.sleep(2)
    stop()


if __name__ == "__main__":
    layout_gpio()
    try:
        print("Planning route...")
        best_order, cheapest_cost = simulated_annealing()
        print("Starting drive in 3 seconds... ")
        time.sleep(3)

        current_position = "start"
        for target in best_order:
            print(f"\n Heading to: {target} ({pickup_nodes[target]})")
            path,cost = astar(current_position, target)
            navigate_path(path)
            # arrived, wait for pickup
            stop()
            color = detect_color()
            expected_color = pickup_nodes[target]
            if color == expected_color:
                print(f"Confirmed {color} at {target}, load cargo...")
            else:
                print(f"Warning: expected {expected_color} but got {color} at {target}")
            time.sleep(2)
            current_position = target

        print("\nAll pickups complete")
        print(f"Colors collected: {detected_pickups}")

    except KeyboardInterrupt:
        print("\n Stopped")
    finally:
        stop()
        kill_cycle()
