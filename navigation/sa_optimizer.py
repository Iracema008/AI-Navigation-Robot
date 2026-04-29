'''Pickup Node Optimization'''

import random
import math

from grid import pickup_nodes
from astar import yabadabadoo, path_cost

def find_neighbors(pickup_nodes):
    #making a copy of current pickup points
    neighbor = pickup_nodes[:]

    # out of the points, choose 2 random indexes to swap
    p_len = range(len(pickup_nodes))
    a, b = random.sample(p_len, 2)
    neighbor[a],neighbor[b] = neighbor[b], neighbor[a]
    return neighbor

def find_cost(pickup_nodes, start="start"):
    curr = start
    total_cost = 0

    for n in pickup_nodes:
        # implement this later
        path = yabadabadoo(curr, n)
        total += path_cost()
        curr = n

    return total_cost

def simulated_annealing(start="start", pickup_nodes=pickup_nodes, temp=10, cooling_rate=0.1, iterations=1000):
    ''' small delta -> higher acceptance
        high temp early on -> more risk
        (and vice versa )
    '''
    curr = list(pickup_nodes.keys())
    random.shuffle(curr)

    curr_cost = find_cost(curr, start)
    best_order = curr[:]
    cheapest_cost = curr_cost

    for a in range (iterations):
        neighbor = find_neighbors(curr)
        neighbor_cost = find_cost(neighbor, start)
        delta = neighbor_cost - curr_cost

        # finds acceptance probability for a worse solution
        prob = math.exp(-delta /temp)
        accept = random.random() < prob

        # if neighbor cost cheaper, go there first
        # or random change of worse solution
        if delta < 0 or accept:
            #update curr to neigbor
            curr = neighbor
            curr_cost = neighbor_cost

        # as itrs cotinue, temp goes down
        # less likely to accept worse solution
        if curr_cost < cheapest_cost:
           best_order = curr[:]
           cheapest_cost = curr_cost

        # cool down temp
        tempt *= (1 - cooling_rate)

    print(f'Best Solution: {best_order}')
    print(f'Best Score: {cheapest_cost}')

    return best_order, cheapest_cost
