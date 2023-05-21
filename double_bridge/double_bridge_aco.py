import random

class Ant:
    def __init__(self, node, speed=1):
        self.node = node
        self.speed = speed

    def choose_path(self, path_short, path_long, alpha):
        # Need to consider the node the ant is currently at. This isn't quite right yet.
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

    def update_pheromone(self, t):
        self.pheromone += rho_is(t-1) + p_is(t-1) * m_i(t-1) + p_js(t-1) * m_j(t-1)
        # ρ_is(t-1) = ρ_is(t-1) + p_is(t-1)m_i(t-1) + p_js(t-1)m_j(t-1), (i=1, j=2; i=2, j=1)
        # OR
        # ρ_il(t) = ρ_il(t-1) + p_il(t-1)m_i(t-1) + p_jl(t-1)m_j(t-r), (i=1, j=2; i=2, j=1)
        # WHERE
        # m_i(t) = p_js(t-1)m_j(t-1) + p_jl(t-r)m_j(t-r)
        pass

class Node:
    def __init__(self, id, ant_count):
        self.id = id
        self.ant_count = ant_count
        self.paths = {}

    def add_path(self, path_name, path):
        self.paths[path_name] = path

    def get_path(self, path_name):
        return self.paths[path_name]

    def update_path(self): 
        for path in self.paths:
            path.update_pheromone()

if __name__ == "__main__":
    # Create the graph
    node1 = Node(id=1, ant_count=10)
    node2 = Node(id=2, ant_count=10)

    path_short = Path(length=10)
    path_long = Path(length=20)

    node1.add_path("short", path_short)
    node1.add_path("long", path_long)
    node2.add_path("short", path_short)
    node2.add_path("long", path_long)

    # Set initial pheromone levels
    path_short.pheromone = 0.1
    path_long.pheromone = 0.1