import random

class Ant:
    def __init__(self, node, speed=1):
        self.node = node
        self.speed = speed

    def choose_path(self, path_short, path_long, alpha):
        total_pheromone = (path_short.pheromone ** alpha) + (path_long.pheromone ** alpha)
        if total_pheromone == 0:
            return random.choice([path_short, path_long])
        
        p_short = (path_short.pheromone ** alpha) / total_pheromone
        if random.random() < p_short:
            return path_short
        else:
            return path_long

class Path:
    def __init__(self, length, pheromone=0):
        self.length = length
        self.pheromone = pheromone

    def update_pheromone(self, p, m):
        # ρ_is(t-1) = ρ_is(t-1) + p_is(t-1)m_i(t-1) + p_js(t-1)m_j(t-1), (i=1, j=2; i=2, j=1)
        # OR
        # ρ_il(t) = ρ_il(t-1) + p_il(t-1)m_i(t-1) + p_jl(t-1)m_j(t-r), (i=1, j=2; i=2, j=1)
        # WHERE
        # m_i(t) = p_js(t-1)m_j(t-1) + p_jl(t-r)m_j(t-r)
        pass

class Graph:
    def __init__(self):
        self.paths = {}

    def add_path(self, path_name, path_length):
        self.paths[path_name] = Path(length=path_length)

    def get_path(self, path_name):
        return self.paths[path_name]
    
    def update_path(self, path_name, p, m):
        self.paths[path_name].update_pheromone(p, m)

class Node:
    def __init__(self, id, ant_count):
        self.id = id
        self.ant_count = ant_count
