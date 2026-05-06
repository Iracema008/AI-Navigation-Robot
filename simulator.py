'''Flask simulator for Nodey warehouse robot'''
'''
Written using Claude for backup simulation 
and testing of pathfinding and pickup logic before 
hardware implementation
'''

from flask import Flask, render_template, request, jsonify
import sys
import os
import random
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from navigation.grid import grid, grid_positions, pickup_nodes
from navigation.astar import astar

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/graph')
def get_graph():
    return jsonify({
        'grid': grid,
        'positions': {k: list(v) for k, v in grid_positions.items()},
        'pickup_nodes': pickup_nodes
    })

@app.route('/api/plan', methods=['POST'])
def plan():
    data = request.json
    selected_pickups = data.get('pickup_nodes', list(pickup_nodes.keys()))
    blocked = data.get('blocked_edges', [])
    blocked_set = {tuple(e) for e in blocked}

    if len(selected_pickups) == 0:
        return jsonify({'error': 'No pickup nodes selected'}), 400

    def find_cost(order, start="start"):
        curr = start
        total = 0
        for n in order:
            path, cost = astar(curr, n, blocked_edges=blocked_set)
            if path is None:
                return float('inf')
            total += cost
            curr = n
        path, cost = astar(curr, "end", blocked_edges=blocked_set)
        if path is None:
            return float('inf')
        total += cost
        return total

    curr = selected_pickups[:]
    random.shuffle(curr)
    curr_cost = find_cost(curr)
    best_order = curr[:]
    best_cost = curr_cost
    temp = 10
    cooling = 0.1

    sa_history = []

    for i in range(1000):
        neighbor = curr[:]
        a, b = random.sample(range(len(neighbor)), 2)
        neighbor[a], neighbor[b] = neighbor[b], neighbor[a]
        ncost = find_cost(neighbor)
        delta = ncost - curr_cost

        if delta < 0 or (temp > 0.001 and random.random() < math.exp(-delta / max(temp, 0.001))):
            curr = neighbor
            curr_cost = ncost

        if curr_cost < best_cost:
            best_order = curr[:]
            best_cost = curr_cost

        temp *= (1 - cooling)

        if i % 100 == 0:
            sa_history.append({'iteration': i, 'cost': best_cost, 'temp': round(temp, 4)})

    legs = []
    current = "start"
    for target in best_order:
        path, cost = astar(current, target, blocked_edges=blocked_set)
        legs.append({
            'from': current,
            'to': target,
            'path': path,
            'cost': cost,
            'is_pickup': target in selected_pickups
        })
        current = target

    path, cost = astar(current, "end", blocked_edges=blocked_set)
    legs.append({
        'from': current,
        'to': 'end',
        'path': path,
        'cost': cost,
        'is_pickup': False
    })

    return jsonify({
        'sa_order': best_order,
        'total_cost': best_cost,
        'legs': legs,
        'sa_history': sa_history
    })

if __name__ == '__main__':
    app.run(debug=True, port=5050)
