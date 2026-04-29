''' Run main logic '''

import time
import RPi.GPIO as GPIO

from motor_controls.moving_motors import forward, left, right, stop
from motor_controls.gpio_setup import layout_gpio, kill_cycle
from sensors.tcrt_5000 import detect_line
from navigation.grid import pickup_nodes
from navigation.sa_optimizer import simulated_annealing
from navigation.astar import astar


# change segement based on tests
SEGMENT_TIME = 2.0
TURN_DURATION = 0.4

# hard coded turn map for now, coming_from, at_junction, going_to -> direction
# Fill this in later to match physical track
TURN_MAP = {
    ("start", "node1", "node3"): "left",
    ("start", "node1", "node4"): "straight",
    ("start", "node2", "node4"): "straight",
    ("start", "node2", "node5"): "right",
    ("node1", "node3", "node6"): "straight",
    ("node1", "node4", "node6"): "left",
    ("node1", "node4", "node7"): "right",
    ("node2", "node4", "node6"): "right",
    ("node2", "node4", "node7"): "left",
    ("node2", "node5", "node7"): "straight",
    # yapp yap yap add the rest later
}

def determine_turn(prev_node, curr_node, next_node):
    return TURN_MAP.get((prev_node, curr_node, next_node), "straight")

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

def follow_line():
    start_time = time.time()

    while time.time() - start_time < SEGMENT_TIME:
        if detect_line():
            forward(70)
        else:
            right(70, 35)
        time.sleep(0.05)
    stop()

def navigate_path(path):
    print(f"  Navigating: {path}")
    for i in range(len(path) - 1):
        current = path[i]
        next_node = path[i + 1]
        prev_node = path[i - 1] if i > 0 else None

        if prev_node:
            direction = determine_turn(prev_node, current, next_node)
            execute_turn(direction)

        follow_line()
        print(f"  Reached: {next_node}")
    stop()



# main
if __name__ == "__main__":
    layout_gpio()

    try:
        print("Planning route...")
        best_order, cheapest_cost, full_route = simulated_annealing()

        print("Starting drive in 3 seconds... ")
        time.sleep(3)

        current_position = "start"
        for target in best_order:
            print(f"\n Heading to: {target} ({pickup_nodes[target]})")
            path = astar(current_position, target)
            navigate_path(path)

            # arrived, wait for pickup
            stop()
            print(f"At {target}, load cargo...")
            time.sleep(2)

            current_position = target

        print("\nAll pickups complete!")

    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        stop()
        kill_cycle()