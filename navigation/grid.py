'''Grid Implementation for "Warehouse" '''

grid = {
    "start": {"node1": 2, "node2":4},
    "node1": {"start": 2, "node3":3, "node4":5},
    "node2": {"start": 4, "node4":2, "node5":3},
    "node3": {"node1":3, "node6":2},
    "node4":{"node1":5, "node2":2, "node6":4, "node7":3},
    "node5":{"node2":3, "node7":2},
    "node6": {"node3":2, "node4":4, "end":3},
    "node7":{"node4":3, "node5":2, "end":2},
    "end": {"node6":3, "node7":2},
}

# Added warehouse grid drawing in hardware reasearch
grid_position = {
    "start": (0,1),
    "node1": (1,2),
    "node2": (1,1),
    "node5": (1,0),

    "node3":(2,2),
    "node4":(2,1),
    "node7":(3,1),

    "node6": (3,2),
    "end":(4,1),
}

# For sure keep rgb for color sensor, yellow TBA
pickup_nodes = {
    "node3": "red",
    "node5": "green",
    "node6": "blue",
    "node7": "yellow",
}