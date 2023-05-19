"""
double_bridge_aco_simulation.py

This script implements a simulation of artificial ants in the double bridge 
experiment, which is a well-known problem in the field of Ant Colony Optimization (ACO). 
The program simulates the behavior of ants choosing between two paths of different lengths 
to a food source, updating pheromone levels on the paths, and converging towards the 
shorter path over time. The ants' behavior is probabilistic, with the chance of choosing 
a path being proportional to the amount of pheromone on the path.
"""

import random

# Define the paths.
# Each path is a dictionary with a length and a pheromone level.
short_path = {'length': 10, 'pheremones': 1}
long_path = {'length': 20, 'pheremones': 1}

def choose_path():
    # Calculate the total amount of pheromone on both paths
    total_path_length = short_path['pheremones'] + long_path['pheremones']

    # Generate a random number between 0 and the total amount of pheromone
    rand_num = random.uniform(0, total_path_length)

    # If the random number is less than the amount of pheromone on the short path,
    # the ant chooses the short path. This means the ant is more likely to choose
    # the path with more pheromone, but it's not guaranteed.
    if rand_num < short_path['pheremone']:
        return short_path
    else:
        return long_path

def update_pheromone(path):
    # The ant deposits pheremone inversely proportional to the length of the path. 
    path['pheremones'] += 1 / path['length']

def run_experiement(n_ants):
    for _ in range(n_ants):
        path = choose_path()

        update_pheromone(path)

for i in range(100):
    run_experiement(10)

print("Short path: ", short_path['pheremones'])
print("Long path: ", long_path['pheremones'])