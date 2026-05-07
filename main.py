''' Run main logic '''

import time
import RPi.GPIO as GPIO

from motor_controls.moving_motors import forward, left, right, stop, backward
from motor_controls.gpio_setup import layout_gpio, kill_cycle
from sensors.tcrt_5000 import detect_line
from sensors.tcs_34725 import detect_color
from sensors.hcsr04 import setup_ultrasonic, obstacle_detected
from navigation.grid import pickup_nodes
from navigation.sa_optimizer import simulated_annealing
from navigation.astar import astar

# change segment based on tests
SEGMENT_TIME = 2.0
TURN_DURATION = 0.4

# hard coded turn map for testing, coming_from, at_junction, going_to -> direction
# Fill this in later to match physical track
TURN_MAP = {
    # start
    ("start", "node1", "node3"): "straight",
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
    #node3
    ("node3", "node6", "end"): "right",
    ("node3", "node7", "node4"): "left",
    ("node3", "node7", "end"): "right",
    # node4
    ("node4", "node7", "node3"): "left",
    ("node4", "node7", "end"): "straight",
    ("node4", "node2", "start"): "right",
    ("node4", "node2", "node5"): "left",
    
    ("node5", "node2", "start"): "right",
    ("node5", "node2", "node4"): "left",
    ("node5", "node7", "node4"): "left",
    ("node5", "node7", "end"): "right",

    ("node6", "end", "node7"): "left",
    ("node6", "node3", "node1"): "straight",
    ("node6", "node3", "node7"): "left",
    # node 7
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

# raised when Nodey sensses an obstacle, the goes back to prev
class ObstacleDetected(Exception):
    def __init__(self, last_node):
        self.last_node = last_node


def determine_turn(prev_node, curr_node, next_node):
    return TURN_MAP.get((prev_node, curr_node, next_node), "straight")

# try to keep speed at 70, else doesn't turn well
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


# reverse along line until color sensor confirms we're back at a node
def reverse_to_last_node():
    print("Obstacle detected: reversing to last node")
    while True:
        color = detect_color()

        if color is not None:
            stop()
            return
        backward(50)
        time.sleep(0.03)


# change to red only  ?
def follow_line_until_color(last_confirmed_node, timeout=10):
    start_time = time.time()

    while time.time() - start_time < timeout:
        if obstacle_detected():
            stop()
            reverse_to_last_node()
            raise ObstacleDetected(last_confirmed_node)

        # Nodey keeps searching for colored nodes 
        color = detect_color()
        if color is not None:
            stop()
            return color
        # otherwise keep using ir
        if detect_line():
            forward(50)
        else:
            right(60, 0)
        time.sleep(0.03)

    stop()

    return None


def navigate_path(path, remaining_targets):
    print(f" Navigating: {path} ")
    
    for i in range(len(path) - 1):
        current = path[i]
        next_node = path[i + 1]
        prev_node = path[i - 1] if i > 0 else None

        if prev_node:
            direction = determine_turn(prev_node, current, next_node)
            execute_turn(direction)
        try:
            color = follow_line_until_color(last_confirmed_node=current)
        except ObstacleDetected as e:
            #last node goes back to main loop & plan again 
            return e.last_node, remaining_targets

        if color:
            print(f"Reached: {next_node}")
        else:
            print(f" Warning: timeout reaching {next_node}")

        if next_node in pickup_nodes and next_node not in detected_pickups:
            detected_pickups.append(next_node)
            print(f"  Pickup detected at {next_node} ({len(detected_pickups)}/{len(pickup_nodes)})")
            stop()
            time.sleep(2)
            if next_node in remaining_targets:
                remaining_targets.remove(next_node)

    stop()
    #  return remaining_targets
    return path[-1], remaining_targets




if __name__ == "__main__":
    setup_ultrasonic()
    layout_gpio()
    try:
        print("Planning route...")
        best_order, cheapest_cost = simulated_annealing()
        print("Starting drive in 3 seconds... ")
        time.sleep(3)

        current_position = "start"
        remaining_targets = list(best_order)

        while remaining_targets:
            target = remaining_targets[0]
            print(f"\n Heading to: {target} ({pickup_nodes[target]})")
            path, cost = astar(current_position, target)

            last_node, remaining_targets = navigate_path(path, remaining_targets)

            # obstacle hit — already back at last_node, recompute from there
            if last_node != path[-1]:
                print(f"  Rerouting from {last_node} toward {target}...")
                current_position = last_node
                continue
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
            if target in remaining_targets:
                remaining_targets.remove(target)

        print("\nAll pickups complete")
        print(f"Colors collected: {detected_pickups}")

    except KeyboardInterrupt:
        print("\n Stopped")
    finally:
        stop()
        kill_cycle()
