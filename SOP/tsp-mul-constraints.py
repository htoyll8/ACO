import numpy as np

class ACO:
    def __init__(self, ants, evaporation_rate, alpha, beta, constraints, iterations, output_file):
        # Initialize parameters
        self.ants = ants  # Number of ants
        self.evaporation_rate = evaporation_rate  # Rate at which pheromone evaporates
        self.alpha = alpha  # Controls the pheromone importance
        self.beta = beta  # Controls the distance importance
        self.constraints = constraints  # List of constraint matrices, one for each ant
        self.iterations = iterations  # Number of iterations
        self.output_file = output_file  # Output file to save the paths

    def fit(self, distances):
        # Fit the ACO algorithm to the problem
        # distances: Distance matrix

        self.distances = distances  # Distance matrix
        num_cities = self.distances.shape[0]  # Number of cities

        # Initialize pheromone on each edge with the same amount
        self.pheromone = np.ones((num_cities, num_cities)) / num_cities

        # Initialize the best path and its distance
        self.best_path = None
        self.best_distance = float('inf')

        # Open the output file to save the paths
        with open(self.output_file, 'w') as f:
            # Iterate the algorithm for a given number of times
            for _ in range(self.iterations):
                all_paths = []

                # Construct paths for all ants
                for i in range(self.ants):
                    # Randomly select the initial city for each ant
                    initial_city = np.random.randint(num_cities)
                    path = [initial_city]  # Start from the randomly selected city
                    unvisited = list(range(1, num_cities))  # List of unvisited cities

                    # Visit all cities
                    while unvisited:
                        current_city = path[-1]  # Current city
                        next_city = self.select_next_city(current_city, self.constraints[i], unvisited)  # Select next city based on pheromone and constraints
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

                # Save the paths for this iteration into the output file
                f.write(f"Iteration: {_ + 1}\n")
                for path, _ in all_paths:
                    f.write(f"{path}\n")
                f.write("\n")

    def select_next_city(self, current_city, constraints, unvisited):
        probabilities = []
        for next_city in unvisited:
            transition_probability = self.pheromone[current_city][next_city] * constraints[current_city][next_city]
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

constraints = np.array([[[0, 1, 1, 0],
                        [1, 0, 1, 1],
                        [1, 1, 0, 1],
                        [0, 1, 1, 0]],

                       [[0, 1, 0, 1],
                        [1, 0, 0, 1],
                        [0, 1, 0, 1],
                        [1, 0, 1, 0]]])

aco = ACO(ants=2, evaporation_rate=0.1, alpha=1, beta=1, constraints=constraints, iterations=100, output_file='paths.txt')
aco.fit(distances)

print(f"Best path: {aco.best_path}")
print(f"Best distance: {aco.best_distance}")

# Define the test instance (distance matrix)
distances = np.array([[0, 10, 15, 20],
                      [10, 0, 35, 25],
                      [15, 35, 0, 30],
                      [20, 25, 30, 0]])

# Define the conflicting constraints for each ant as a list of matrices
constraints = [
    np.array([[0, 1, 1, 0],
              [1, 0, 0, 1],
              [0, 1, 0, 1],
              [1, 0, 1, 0]]),
    np.array([[0, 1, 0, 1],
              [1, 0, 1, 0],
              [0, 1, 0, 1],
              [1, 0, 1, 0]]),
    np.array([[1, 0, 1, 0],
              [0, 1, 1, 0],
              [1, 1, 0, 1],
              [0, 0, 1, 0]]),
    np.array([[0, 1, 0, 1],
              [1, 0, 1, 0],
              [0, 1, 0, 1],
              [1, 0, 1, 0]]),
    np.array([[0, 0, 1, 0],
              [0, 0, 1, 0],
              [1, 1, 0, 1],
              [0, 0, 1, 0]]),
    np.array([[0, 1, 1, 0],
              [1, 0, 1, 0],
              [0, 1, 0, 1],
              [1, 0, 1, 0]]),
    np.array([[1, 0, 1, 0],
              [0, 1, 1, 0],
              [1, 1, 0, 1],
              [0, 0, 1, 0]]),
    np.array([[0, 0, 1, 0],
              [0, 0, 1, 0],
              [1, 1, 0, 1],
              [0, 0, 1, 0]]),
    np.array([[0, 1, 1, 0],
              [1, 0, 1, 0],
              [0, 1, 0, 1],
              [1, 0, 1, 0]]),
    np.array([[1, 0, 1, 0],
              [0, 1, 1, 0],
              [1, 1, 0, 1],
              [0, 0, 1, 0]])
]

# Create an ACO instance with conflicting constraints
aco = ACO(ants=10, evaporation_rate=0.1, alpha=1, beta=1, constraints=constraints, iterations=100, output_file='paths.txt')

# Run the ACO algorithm
aco.fit(distances)

# Print the best path and its distance
print(f"Best path: {aco.best_path}")
print(f"Best distance: {aco.best_distance}")
