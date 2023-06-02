import numpy as np

class ACO:
    def __init__(self, ants, evaporation_rate, alpha, beta, iterations):
        # Initialize parameters
        self.ants = ants  # Number of ants
        self.evaporation_rate = evaporation_rate  # Rate at which pheromone evaporates
        self.alpha = alpha  # Controls the pheromone importance
        self.beta = beta  # Controls the distance importance
        self.iterations = iterations  # Number of iterations

    def fit(self, distances, constraints):
        # Fit the ACO algorithm to the problem
        # distances: Distance matrix
        # constraints: Constraint matrix

        self.distances = distances  # Distance matrix
        self.constraints = constraints  # Constraint matrix
        num_cities = self.distances.shape[0]  # Number of cities

        # Initialize pheromone on each edge with the same amount
        self.pheromone = np.ones((num_cities, num_cities)) / num_cities

        # Initialize the best path and its distance
        self.best_path = None
        self.best_distance = float('inf')

        # Iterate the algorithm for a given number of times
        for _ in range(self.iterations):
            all_paths = []

            # Construct paths for all ants
            for _ in range(self.ants):
                path = [0]  # Start from the first city
                unvisited = list(range(1, num_cities))  # List of unvisited cities

                # Visit all cities
                while unvisited:
                    current_city = path[-1]  # Current city
                    next_city = self.select_next_city(current_city, unvisited)  # Select next city based on pheromone and constraints
                    path.append(next_city)  # Move to the next city
                    unvisited.remove(next_city)  # Remove the next city from the list of unvisited cities

                path.append(0)  # Return to the first city to complete the loop
                distance = self.get_distance(path)  # Calculate the total distance of the path

                # Update the best path and distance if the current path is better
                if distance < self.best_distance:
                    self.best_distance = distance
                    self.best_path = path

                all_paths.append((path, distance))  # Append the path and distance to the list of all paths

            self.update_pheromones(all_paths)  # Update pheromones on all paths

    def select_next_city(self, current_city, unvisited):
        probabilities = []
        for next_city in unvisited:
            transition_probability = self.pheromone[current_city][next_city] * self.constraints[current_city][next_city]
            probabilities.append(transition_probability)

        if np.sum(probabilities) == 0 or np.isnan(np.sum(probabilities)):
            # If all probabilities are zero or invalid, assign equal probabilities to all unvisited cities
            probabilities = np.ones(len(unvisited)) / len(unvisited)
        else:
            # Normalize the probabilities
            probabilities /= np.sum(probabilities)

        next_city = np.random.choice(unvisited, p=probabilities)
        return next_city

    def update_pheromones(self, paths):
        # Update the pheromone levels on the edges
        # paths: List of paths taken by the ants

        self.pheromone *= (1 - self.evaporation_rate)  # Evaporate pheromone on all edges

        # Update pheromones on all paths
        for path, distance in paths:
            for i in range(len(path) - 1):
                from_city = path[i]  # Starting city of the edge
                to_city = path[i + 1]  # Ending city of the edge
                self.pheromone[from_city][to_city] += 1.0 / distance  # Increase the pheromone level on the edge

    def get_distance(self, path):
        # Calculate the total distance of a given path
        # path: Path taken by an ant

        distance = 0

        # Calculate the distance for each edge in the path and sum them up
        for i in range(len(path) - 1):
            from_city = path[i]  # Starting city of the edge
            to_city = path[i + 1]  # Ending city of the edge
            distance += self.distances[from_city][to_city]  # Add the distance of the edge to the total distance

        return distance

distances = np.array([[0, 10, 15, 20],
                      [10, 0, 35, 25],
                      [15, 35, 0, 30],
                      [20, 25, 30, 0]])

constraints = np.array([[0, 1, 1, 0],
                        [1, 0, 1, 1],
                        [1, 1, 0, 1],
                        [0, 1, 1, 0]])

aco = ACO(ants=10, evaporation_rate=0.1, alpha=1, beta=1, iterations=100)
aco.fit(distances, constraints)


print(f"Best path: {aco.best_path}")
print(f"Best distance: {aco.best_distance}")

distances = np.array([[0, 10, 15, 20],
                      [10, 0, 35, 25],
                      [15, 35, 0, 30],
                      [20, 25, 30, 0]])

constraints = np.array([[0, 1, 1, 0],
                        [1, 0, 0, 1],
                        [0, 1, 0, 1],
                        [1, 0, 1, 0]])

aco = ACO(ants=10, evaporation_rate=0.1, alpha=1, beta=1, iterations=100)
aco.fit(distances, constraints)

print(f"Best path: {aco.best_path}")
print(f"Best distance: {aco.best_distance}")


