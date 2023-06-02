import numpy as np

class ACO:
    def __init__(self, ants, evaporation_rate, alphas, betas, iterations):
        # Initialize parameters
        self.ants = ants  # number of ants
        self.evaporation_rate = evaporation_rate  # rate at which pheromone evaporates
        self.alphas = alphas  # controls the pheromone importance - now a list.
        self.betas = betas  # controls the distance importance - now a list.
        self.iterations = iterations  # number of iterations

    def fit(self, distances):
        self.distances = distances  # distance matrix
        # initialize pheromone on each path with the same amount
        self.pheromone = np.ones(self.distances.shape) / len(distances)
        # initialize the best paths and their distances
        self.best_distances = []
        # The indices of the best path in the all_paths list
        self.best_path_indices = []

        # iterate the algorithm for a given number of times
        for _ in range(self.iterations):
            # construct the paths for all ants
            all_paths = self.construct_paths()
            # deposit pheromones on all paths
            self.deposit_pheromones(all_paths)
            # select the shortest paths among all ants
            sorted_paths = sorted(all_paths, key=lambda x: x[1])
            # Retrieve the top-k best paths from the all_paths array.
            self.best_paths = [path for path, _ in sorted_paths[:self.ants]]
            self.best_distances = [distance for _, distance in sorted_paths[:self.ants]]

    def construct_paths(self):
        all_paths = []
        for i in range(self.ants):
            # set the alpha and beta for this ant
            alpha = self.alphas[i]
            beta = self.betas[i]
            # each ant starts from a randomly selected city
            path = [np.random.randint(0, self.distances.shape[0])]
            # and visits all other cities
            while len(path) < self.distances.shape[0]:
                # the next city is selected based on the amount of pheromone and distance
                probabilities = self.get_probabilities(path[-1], path, alpha, beta)
                next_city = np.random.choice(range(self.distances.shape[0]), p=probabilities)
                path.append(next_city)
            # after visiting all cities, return to the first one
            path.append(path[0])
            # add the path and its total distance to the list of all paths
            all_paths.append((path, self.get_distance(path)))
        return all_paths

    def get_probabilities(self, city, visited, alpha, beta):
        # Create a copy of the pheromone trail from the current city to all other cities
        pheromone = self.pheromone[city, :].copy()

        # Create a copy of the distances from the current city to all other cities
        distances = self.distances[city, :].copy()

        # Create a mask array (of the same shape as 'pheromone') with all elements set to True
        # This mask will be used to indicate which cities are valid (not visited) 
        mask = np.ones(pheromone.shape, dtype=bool)

        # Update the mask array to set the visited cities to False (i.e., these cities are not valid)
        mask[visited] = False

        # Set the pheromone level to 0 for the visited cities
        pheromone[visited] = 0

        # Compute the denominator of the probability formula
        # This is done only for the valid (not visited) cities
        # The formula takes into account both the pheromone level and the distance
        # The pheromone level is raised to the power of 'beta' and the distance is raised to the power of 'alpha'
        # Note: We add a small constant (1e-10) to the distance to avoid division by zero
        denominator = np.sum((pheromone[mask]**beta) * ((1.0 / (distances[mask] + 1e-10))**alpha))

        # Create an array for the probabilities with the same shape as 'pheromone', and initialize all elements to 0
        probabilities = np.zeros_like(pheromone)

        # Compute the probabilities for the valid (not visited) cities
        # The formula is the same as for the denominator, but each term is divided by the denominator
        # This way, the sum of all probabilities will be 1
        probabilities[mask] = (pheromone[mask]**beta) * ((1.0 / (distances[mask] + 1e-10))**alpha) / denominator

        # Return the probabilities array
        return probabilities

    def deposit_pheromones(self, paths):
        # evaporate the pheromone on each path
        self.pheromone * (1 - self.evaporation_rate)
        for path, distance in paths:
            for move in zip(path[:-1], path[1:]):
                # increase the pheromone on the path of each ant
                self.pheromone[move] += 1.0 / self.distances[move]

    def get_distance(self, path):
        # compute the total distance of the path
        return sum(self.distances[move] for move in zip(path[:-1], path[1:]))

distances = np.array([[0, 10, 15, 20],
                      [10, 0, 35, 25],
                      [15, 35, 0, 30],
                      [20, 25, 30, 0]])

alphas = [1, 1, 0.5, 0.5, 2, 2, 1.5, 1.5, 1, 1]
betas = [1, 2, 1, 2, 1, 0.5, 2, 1, 1.5, 0.5]

aco = ACO(ants=10, evaporation_rate=0.1, alphas=alphas, betas=betas, iterations=100)
aco.fit(distances)

print("Best Paths:")
for path in aco.best_paths:
    print(path)

print("Best Distances:")
for distance in aco.best_distances:
    print(distance)
