'''General path planning for Nodey'''

import math
import heapq

from grid import grid, grid_positions


def heuristic(node, goal):
    '''Euclidean distance between two nodes using grid_positions'''
    x1, y1 = grid_positions[node]
    x2, y2 = grid_positions[goal]
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def astar(start, goal, blocked_edges=None):
    '''A* pathfinding on the warehouse grid'''
    if blocked_edges is None:
        blocked_edges = set()
    
    # priority queue (f_score, node)
    open_list = []
    heapq.heappush(open_list, (0, start))

    #distance from start node to current node 
    g_score = {start: 0}

    # track which nodes where we came from to reconstruct path
    came_from = {}

    # tracks which nodes have been visited
    visitied = set()

    while open_list:
        f, current = heapq.heappop(open_list)

        # reached the goal, reconstruct path
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path, g_score[goal]
        
        # skip if we already visited this node
        if current in visitied:
            continue
        visitied.add(current)

        # check neighbors of the current node 
        for neighbor, cost in grid[current].items():
            #skip if this edge is blocked
            if (current, neighbor) in blocked_edges or (neighbor, current) in blocked_edges:
                continue

            new_g = g_score[current] + cost

            #only proceed if this is the most efficient path to the neighbor 
            if new_g < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = new_g
                f_score = new_g + heuristic(neighbor, goal)
                came_from[neighbor] = current
                heapq.heappush(open_list, (f_score, neighbor))
    
    # no path found
    return None, float('inf') 


# test
if __name__ == "__main__":
    path, cost = astar("start", "end")
    print("Path:", path)
    print("Cost:", cost)

    #path to pickup node
    path, cost = astar("start", "node3")
    print("Path to node3:", path)
    print("Cost to node3:", cost)

    # blocked edge test
    blocked_edges = {("node2", "node4")}
    path, cost = astar("start", "node7", blocked_edges=blocked_edges)
    print("Path with edge 2-4 blocked:", path)
    print("Cost with edge 2-4 blocked:", cost)


    # blocked edge test
    blocked_edges = {("node2", "node4"), ("node1", "node3")}
    path, cost = astar("start", "node7", blocked_edges=blocked_edges)
    print("Path with edge 2-4 & 1-3 blocked:", path)
    print("Cost with edge 2-4 & 1-3 blocked:", cost)

    # compare with no blocked edges
    path, cost = astar("start", "node7")
    print("Path with no blocked edges:", path)
    print("Cost with no blocked edges:", cost)
