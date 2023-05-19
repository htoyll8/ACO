class Ant:
    def __init__(self, node, speed=1):
        self.node = node
        self.speed = speed

    def choose_path(self):
        pass

class Path:
    def __init__(self, length, pheromone=0):
        self.length = length
        self.pheromone = pheromone

    def update_pheromone(self):
        pass

class Graph: 
    def __init__(self):
        self.paths = {}

    def add_path(self, path_name, path_length):
        self.paths[path_name] = Path(length=path_length)

    def get_path(self, path_name):
        return self.paths[path_name]
    
    def update_path(self, path_name):
        self.paths[path_name].update_pheromone()

class Node:
    def __init__(self, ant_count):
        self.ant_count = ant_count