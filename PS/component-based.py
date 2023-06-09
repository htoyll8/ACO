import inspect
import random
from collections import deque
from itertools import combinations

class PetriNet:
    def __init__(self):
        """
        Initializes an empty Petri net.
        """
        self.places = set()  # Dictionary to store places and their token counts
        self.place_markings = {}  # Dictionary to store place markings
        self.transitions = set()  # Set to store transition nodes
        self.edges = {}  # Dictionary to store edge weights between nodes

    def add_place(self, place, markings=0):
        """
        Adds a place to the Petri net.

        Args:
            place (str): Name of the place.
            marking (int): Initial marking for the place (default is 0).
        """
        self.places.add(place)  # Adds the place to the set of places
        self.place_markings[place] = markings  # Initializes the marking of the place

    def add_transition(self, transition):
        """
        Adds a transition to the Petri net.

        Args:
            transition (str): Name of the transition.
        """
        self.transitions.add(transition)  # Adds the transition to the set of transitions

    def add_edge(self, node1, node2, weight=1):
        """
        Adds an edge between two nodes in the Petri net.

        Args:
            node1 (str): Name of the first node.
            node2 (str): Name of the second node.
            weight (int): Weight of the edge (default is 1).
        """
        if node1 in self.places and node2 not in self.transitions:
            raise ValueError(f"Invalid node: {node1}")  # Error handling for invalid node

        if node1 in self.transitions and node2 not in self.places:
            raise ValueError(f"Invalid node: {node2}")  # Error handling for invalid node

        if node1 in self.edges:
            self.edges[node1][node2] = weight  # Adds node2 with the specified weight as an outgoing edge from node1
        else:
            self.edges[node1] = {node2: weight}  # Creates a new dictionary for the outgoing edges from node1 with node2 and weight

    def execute_transition(self, transition, place_markings):
        """
        Executes a transition in the Petri net.

        Args:
            transition (str): Name of the transition.
            place_markings (dict): Dictionary mapping place names to their markings.

        Returns:
            dict: Updated place markings after executing the transition.
        """
        # Create a copy of the place markings
        updated_place_markings = place_markings.copy()

        # Find all of the inputs to the transition
        inputs = [place for place, edges in self.edges.items() if edges.get(transition) is not None]

        # Check if each input place has enough markings
        for input_place in inputs:
            edge_weight = self.edges[input_place][transition]
            if updated_place_markings[input_place] < edge_weight:
                # raise ValueError(f"Not enough tokens in place {input_place} to fire transition {transition}.")
                return place_markings  # Transition cannot be fired, return the original markings

        output_place = next(iter(self.edges[transition].keys()))

        # Consume tokens from input places
        for input_place in inputs:
            input_edge_weight = self.edges[input_place][transition]
            output_edge_weight = self.edges[transition][output_place]
            updated_place_markings[input_place] -= input_edge_weight
            # Add tokens to the output place
            updated_place_markings[output_place] += output_edge_weight
        
        return updated_place_markings

    def enabled_edges(self, place_markings):
        """
        Returns a list of enabled transitions based on the given place.

        Args:
            place (str): Name of the place.
            place_marking (int): Marking of the place.

        Returns:
            list: List of enabled edges.
        """
        enabled_edges = []

        for place, marking in place_markings.items():
            if marking != 0 and place in self.edges:
                for destination_node, weight in self.edges[place].items():
                    if marking >= weight and destination_node not in enabled_edges:
                        enabled_edges.append(destination_node)

        return enabled_edges

    def get_markings(self):
        """
        Retrieves the current markings of all place nodes in the Petri net.

        Returns:
            dict: A dictionary mapping place names to their current markings.
        """
        return self.place_markings.copy()  # Returns a copy of the dictionary containing the place markings

def construct_petri(components, user_provided_signature):
    """
    Constructs a Petri net based on the given components.

    Args:
        components (list): List of components.
        user_provided_signature (function): User-provided signature as a Python function.

    Returns:
        PetriNet: Constructed Petri net.
    """
    petri_net = PetriNet()  # Create an empty Petri net

    signature = inspect.signature(user_provided_signature)
    parameters = {}
    for param in signature.parameters.values():
        param_name = param.name
        param_type = param.annotation.__name__
        if param_type not in parameters:
            parameters[param_type] = []
        parameters[param_type].append(param_name)

    for component in components:
        inputs = get_inputs(component)  # Get the input types for the component
        output = get_outputs(component)  # Get the output type for the component

        petri_net.add_transition(component)  # Add a transition for the component

        for input_type in inputs:
            if input_type not in petri_net.places:
                petri_net.add_place(input_type)  # Add the place if it doesn't exist already

                if input_type in parameters:
                    count = len(parameters[input_type])
                    petri_net.place_markings[input_type] += count  # Increment the token count of the place by the count

            petri_net.add_edge(input_type, component, weight=len(inputs[input_type]))  # Add an edge from the input type to the component

        if output not in petri_net.places:
            petri_net.add_place(output)  # Add the place for the output type if it doesn't exist already

        petri_net.add_edge(component, output)  # Add an edge from the component to the output type

    return petri_net

def get_inputs(component):
    """
    Extracts the input types from the given component.

    Args:
        component (function): Component representing a function from the API.

    Returns:
        dict: Dictionary mapping input types to a list of arguments of that type.
    """
    inputs = {}
    
    # Extract the input types from the component's signature
    signature = inspect.signature(component)
    parameters = signature.parameters.values()

    for parameter in parameters:
        input_type = parameter.annotation
        
        # Skip parameters with no annotation
        if input_type is inspect.Parameter.empty:
            continue
        
        # Convert the input_type to its string representation
        input_type_str = input_type.__name__
        
        # Add the parameter to the corresponding input type
        if input_type_str in inputs:
            inputs[input_type_str].append(parameter.name)
        else:
            inputs[input_type_str] = [parameter.name]
    
    return inputs

def get_outputs(component):
    """
    Get the output type of a component.

    Args:
        component: The component to inspect.

    Returns:
        The output type name of the component, or None if not found.
    """
    output_type = "None"

    # Check if the component is a function or method
    if inspect.isfunction(component) or inspect.ismethod(component):
        signature = inspect.signature(component)
        return_type = signature.return_annotation
        if return_type != inspect.Signature.empty:
            output_type = return_type.__name__

    return output_type

# Reachbility graph.

class ReachabilityGraph:
    def __init__(self):
        self.nodes = set()
        self.edges = {}

    def add_node(self, node):
        self.nodes.add(tuple(node.items()))

    def add_edge(self, source, transition, destination):
        if source not in self.edges:
            self.edges[source] = {}
        self.edges[source][transition] = destination

def construct_reachability_graph(petri_net):
    reachability_graph = ReachabilityGraph()
    initial_markings = petri_net.place_markings.copy()
    worklist = deque([initial_markings])
    visited_markings = set()  # Keep track of visited markings
    visited_edges = set()  # Keep track of visited edges

    while worklist:
        current_markings = worklist.popleft()
        current_markings_tuple = tuple(current_markings.items())

        if current_markings_tuple in visited_markings:
            continue  # Skip if the current marking has already been visited

        visited_markings.add(current_markings_tuple)  # Add current marking to visited markings
        reachability_graph.add_node(current_markings)

        enabled_transitions = petri_net.enabled_edges(current_markings)

        for transition in enabled_transitions:
            successor_markings = petri_net.execute_transition(transition, current_markings)
            successor_markings_tuple = tuple(successor_markings.items())

            if successor_markings_tuple == current_markings_tuple:
                continue  # Skip if the successor marking is the same as the current marking

            edge = (current_markings_tuple, transition, successor_markings_tuple)
            if edge in visited_edges:
                continue  # Skip if the edge has already been visited

            visited_edges.add(edge)  # Add edge to visited edges
            reachability_graph.add_node(successor_markings)
            print("Current marking: ", current_markings_tuple, "Succesor markings: ", successor_markings_tuple)
            reachability_graph.add_edge(current_markings_tuple, transition, successor_markings_tuple)

            worklist.append(successor_markings)

    return reachability_graph

class Ant:
    def __init__(self, start_marking):
        self.current_marking = start_marking
        self.path = []
    
    def update_current_marking(self, marking):
        if isinstance(marking, tuple):
            self.current_marking = dict(marking)
        else:
            self.current_marking = marking
    
    def add_transition_to_path(self, transition):
        self.path.append(transition)

def ant_colony_optimization(reachability_graph, start_marking, desired_marking, num_ants=10, num_iterations=100, alpha=1.0, beta=2.0, evaporation_rate=0.5):
    pheromone = initialize_pheromone(reachability_graph)  # Initialize pheromone matrix
    best_path = None
    best_path_length = float('inf')
    
    for _ in range(num_iterations):
        paths = []
        
        # Construct paths for all ants
        for _ in range(num_ants):
            ant = Ant(start_marking)
            print("Pheromone upper parameter: ", pheromone)
            construct_path(reachability_graph, ant, pheromone, desired_marking, alpha, beta)
            paths.append(ant.path)

            if not best_path:
                best_path = ant.path
                best_path_length = len(ant.path)
                best_marking = ant.current_marking

            if hamming_distance(ant.current_marking, desired_marking) < hamming_distance(best_marking, desired_marking) or (ant.path and len(ant.path) < best_path_length):
                print("Best path intermediate:", best_path)
                best_path = ant.path
                best_path_length = len(ant.path)
                best_marking = ant.current_marking
        
        # Update pheromone matrix
        pheromone = update_pheromone(pheromone, paths, evaporation_rate)
    
    return best_path

def initialize_pheromone(reachability_graph):
    pheromone = {}
    print("Edges: ", reachability_graph.edges)
    for source in reachability_graph.nodes:
        print("Source: ", source)
        for transition in reachability_graph.edges[source]:
            pheromone[transition] = 1.0
    print("Pheremone: ", pheromone)
    return pheromone

def construct_path(reachability_graph, ant, pheromone, desired_marking, alpha, beta):
    while ant.current_marking != desired_marking:
        print("MARKING: ", ant.current_marking)
        current_marking_tuple = tuple(ant.current_marking.items())
        enabled_transitions = reachability_graph.edges[current_marking_tuple]
        probabilities = calculate_transition_probabilities(enabled_transitions, pheromone, alpha, beta)
        transition = select_transition(probabilities)
        print("Selected transition: ", transition)
        
        if transition is None:
            break
        
        successor_marking = reachability_graph.edges[current_marking_tuple][transition]
        ant.add_transition_to_path(transition)
        ant.update_current_marking(successor_marking)

def hamming_distance(marking1, marking2):
    distance = 0
    for place in marking1:
        if marking1[place] != marking2[place]:
            distance += 1
    return distance

def calculate_transition_probabilities(enabled_transitions, pheromone, alpha, beta):
    total_pheromone = 0.0
    probabilities = {}

    print("Pheromone: ", pheromone)
    for transition, weight in pheromone.items():
        total_pheromone += weight ** alpha

    print("Enabled transitions: ", enabled_transitions)
    for transition in enabled_transitions:
        probability = (pheromone[transition] ** alpha) / total_pheromone
        probabilities[transition] = probability

    print("Total pheromone: ", total_pheromone)
    print("Probabilities: ", probabilities)
    return probabilities

def select_transition(probabilities):
    random_value = random.random()
    print("Random value: ", random_value)
    cumulative_probability = 0.0
    for transition, probability in probabilities.items():
        cumulative_probability += probability
        if random_value <= cumulative_probability:
            return transition
    return None

def update_pheromone(pheromone, paths, evaporation_rate):
    print("Paths: ", paths)
    print("Evaporation rate: ", evaporation_rate)
    print("Pheromone: ", pheromone)

    # Evaporate pheromone on all transitions
    for transition in pheromone:
        pheromone[transition] *= (1.0 - evaporation_rate)  # Evaporate pheromone on each transition

    # Deposit pheromone on the transitions in the paths
    for path in paths:
        path_length = len(path)
        for i in range(path_length - 1):
            transition = path[i]  # Assuming transitions are used as path elements
            if transition in pheromone:
                pheromone[transition] += 1.0 / path_length  # Deposit pheromone on the transition

    return pheromone

def find_paths(reachability_graph, start_marking, desired_marking):
    paths = []

    def backtrack(path, current_marking, visited_markings):
        current_marking = dict(current_marking)

        if current_marking == desired_marking:
            paths.append(path[:])
            return

        if isinstance(current_marking, dict):
            current_marking = tuple(current_marking.items())

        enabled_transitions = reachability_graph.edges.get(current_marking, {})

        for transition, successor_marking in enabled_transitions.items():
            path.append(transition)
            new_visited_markings = set(visited_markings)  # Create a new set for each recursive call
            if successor_marking not in new_visited_markings:
                new_visited_markings.add(successor_marking)
                # print("Exploring transition:", transition)  # Add print statement
                backtrack(path, successor_marking, new_visited_markings)
            path.pop()

    visited_markings = set()
    visited_markings.add(tuple(start_marking.items()))
    backtrack([], start_marking, visited_markings)
    return paths

def generate_program_sketch(transition, num_parameters):
    # Implement the logic to generate the program sketch based on the transition and parameters
    parameters = [f"x_{i+1}" for i in range(num_parameters)]
    program_sketch = f"{transition}({', '.join(parameters)})"
    return program_sketch

def pretty_print_edges(edges):
    print("Edges: ")
    for marking, transitions in edges.items():
        print(marking, end=": ")
        print({transition: successor_marking for transition, successor_marking in transitions.items()})

# Test cases

def test_execute_transition():
    petri_net = PetriNet()

    # Add places
    petri_net.add_place("P1", markings=2)
    petri_net.add_place("P2", markings=1)
    petri_net.add_place("P3")

    # Add transitions
    petri_net.add_transition("T1")

    # Add edges
    petri_net.add_edge("P1", "T1", weight=2)
    petri_net.add_edge("T1", "P2", weight=1)

    # Set initial markings
    initial_markings = {"P1": 2, "P2": 1, "P3": 0}

    # Execute the transition
    updated_markings = petri_net.execute_transition("T1", initial_markings)
    print("Updated markings: ", updated_markings)

    # Check the updated markings
    expected_markings = {"P1": 0, "P2": 2, "P3": 0}

    assert updated_markings == expected_markings

    # Add places
    petri_net.add_place("P1", markings=2)
    petri_net.add_place("P2", markings=1)
    petri_net.add_place("P3", markings=1)

    # Add transitions
    petri_net.add_transition("T1")

    # Add edges
    petri_net.add_edge("P1", "T1", weight=2)
    petri_net.add_edge("P3", "T1", weight=1)
    petri_net.add_edge("T1", "P2", weight=1)

    # Set initial markings
    initial_markings = {"P1": 2, "P2": 1, "P3": 1}

    # Execute the transition
    updated_markings = petri_net.execute_transition("T1", initial_markings)

    # Check the updated markings
    expected_markings = {"P1": 0, "P2": 3, "P3": 0}

    assert updated_markings == expected_markings

    print("\u2705 Execute transitions tests passed!")

def test_construct_petri():
    def example_function(x: int, y: str, z: float) -> int:
        pass

    components = [example_function]  # Example list of components
    
    petri_net = construct_petri(components, example_function)
    
    # Verify the places and their initial markings
    expected_marking = {
        'int': 1,
        'str': 1,
        'float': 1,
    }

    # Check the initial markings
    assert petri_net.get_markings() == expected_marking
    
    print("\u2705 Construct petri net tests passed!")

def test_get_inputs():
    # Define a sample component
    def sample_component(x: int, y: str, z: float):
        pass

    # Get the inputs of the sample component
    inputs = get_inputs(sample_component)

    # Expected inputs: {'int': ['x'], 'str': ['y'], 'float': ['z']}
    expected_inputs = {'int': ['x'], 'str': ['y'], 'float': ['z']}

    # Compare the actual and expected inputs
    assert inputs == expected_inputs, "Test case failed"

    print("\u2705 Get inputs tests passed!")

def test_get_outputs():
    def add(a: int, b: int) -> int:
        return a + b

    def multiply(a: float, b: float) -> float:
        return a * b

    def no_return_type(a: str):
        return len(a)

    assert get_outputs(add) == 'int'
    assert get_outputs(multiply) == 'float'
    assert get_outputs(no_return_type) == 'None'
    print("\u2705 Get outputs tests passed!")

def test_enabled_edges():
    petri_net = PetriNet()

    # Add places
    petri_net.add_place("P1", markings=2)
    petri_net.add_place("P2", markings=1)
    petri_net.add_place("P3")

    # Add transitions
    petri_net.add_transition("T1")
    petri_net.add_transition("T2")
    petri_net.add_transition("T3")

    # Add edges
    petri_net.add_edge("P1", "T1", weight=2)
    petri_net.add_edge("P2", "T1", weight=1)
    petri_net.add_edge("P2", "T2", weight=1)
    petri_net.add_edge("P3", "T3", weight=2)

    # Set place markings
    place_markings = {"P1": 2, "P2": 1, "P3": 0}

    # Get enabled edges
    enabled_edges = petri_net.enabled_edges(place_markings)

    # Check the enabled edges
    expected_enabled_edges = ["T1", "T2"]
    assert enabled_edges == expected_enabled_edges

    print("\u2705 Enabled edges tests passed!")

def test_construct_reachability_graph():
    # Create a Petri net
    petri_net = PetriNet()

    # Add places to the Petri net
    petri_net.add_place("P1", markings=1)
    petri_net.add_place("P2", markings=0)
    petri_net.add_place("P3", markings=0)

    # Add transitions to the Petri net
    petri_net.add_transition("T1")
    petri_net.add_transition("T2")

    # Add edges between nodes in the Petri net
    petri_net.add_edge("P1", "T1")
    petri_net.add_edge("T1", "P2")
    petri_net.add_edge("P2", "T2")
    petri_net.add_edge("T2", "P3")

    # Set the desired output type
    desired_output_type = int

    # Construct the reachability graph
    reachability_graph = construct_reachability_graph(petri_net)

    # Verify the correctness of the reachability graph
    assert len(reachability_graph.nodes) == 3  # Expected node count
    assert len(reachability_graph.edges) == 2  # Expected edge count

    expected_nodes = [
        {"P1": 1, "P2": 0, "P3": 0},
        {"P1": 0, "P2": 1, "P3": 0},
        {"P1": 0, "P2": 0, "P3": 1}
    ]

    for node in expected_nodes:
        assert tuple(node.items()) in reachability_graph.nodes  # Check if the node exists in the reachability graph

    print("\u2705 Construct reachability graph tests passed!")

# Testing the find_paths function
def test_find_paths():
    # Create a Petri net
    petri_net = PetriNet()

    # Add places to the Petri net
    petri_net.add_place("P1", markings=1)
    petri_net.add_place("P2", markings=0)
    petri_net.add_place("P3", markings=0)

    # Add transitions to the Petri net
    petri_net.add_transition("T1")
    petri_net.add_transition("T2")

    # Add edges between nodes in the Petri net
    petri_net.add_edge("P1", "T1")
    petri_net.add_edge("T1", "P2")
    petri_net.add_edge("P2", "T2")
    petri_net.add_edge("T2", "P3")

    # Construct the reachability graph
    reachability_graph = construct_reachability_graph(petri_net)

    # Test case 1: Find paths from initial marking to {"P1": 0, "P2": 0, "P3": 1}
    start_marking = {"P1": 1, "P2": 0, "P3": 0}
    desired_marking = {"P1": 0, "P2": 0, "P3": 1}
    paths = find_paths(reachability_graph, start_marking, desired_marking)
    assert len(paths) == 1
    assert paths[0] == ["T1", "T2"]

    # Test case 2: Find paths from initial marking to {"P1": 0, "P2": 1, "P3": 0}
    start_marking = {"P1": 1, "P2": 0, "P3": 0}
    desired_marking = {"P1": 0, "P2": 1, "P3": 0}

    # Create a Petri net
    petri_net = PetriNet()

    # Add places to the Petri net
    petri_net.add_place("P1", markings=1)
    petri_net.add_place("P2", markings=0)
    petri_net.add_place("P3", markings=0)
    petri_net.add_place("P4", markings=0)
    petri_net.add_place("P5", markings=0)

    # Add transitions to the Petri net
    petri_net.add_transition("T1")
    petri_net.add_transition("T2")
    petri_net.add_transition("T3")
    petri_net.add_transition("T4")

    # Add edges between nodes in the Petri net
    petri_net.add_edge("P1", "T1")
    petri_net.add_edge("T1", "P2")
    petri_net.add_edge("P2", "T2")
    petri_net.add_edge("T2", "P3")
    petri_net.add_edge("P3", "T3")
    petri_net.add_edge("T3", "P4")
    petri_net.add_edge("P4", "T4")
    petri_net.add_edge("T4", "P5")

    # Construct the reachability graph
    reachability_graph = construct_reachability_graph(petri_net)

    # Test case 1: Find paths from initial marking to {"P1": 0, "P2": 0, "P3": 1, "P4": 0, "P5": 1}
    start_marking = {"P1": 1, "P2": 0, "P3": 0, "P4": 0, "P5": 0}
    desired_marking = {"P1": 0, "P2": 0, "P3": 1, "P4": 0, "P5": 0}
    paths = find_paths(reachability_graph, start_marking, desired_marking)
    assert len(paths) == 1
    assert paths[0] == ["T1", "T2"]

    # Test case 2: Find paths from initial marking to {"P1": 0, "P2": 1, "P3": 0, "P4": 1, "P5": 0}
    start_marking = {"P1": 1, "P2": 0, "P3": 0, "P4": 0, "P5": 0}
    desired_marking = {"P1": 0, "P2": 0, "P3": 0, "P4": 0, "P5": 1}
    paths = find_paths(reachability_graph, start_marking, desired_marking)
    assert len(paths) == 1
    assert paths[0] == ["T1", "T2", "T3", "T4"]

    # Create a Petri net
    petri_net = PetriNet()

    # Add places to the Petri net
    petri_net.add_place("P1", markings=1)
    petri_net.add_place("P2", markings=0)
    petri_net.add_place("P3", markings=0)
    petri_net.add_place("P4", markings=0)
    petri_net.add_place("P5", markings=0)

    # Add transitions to the Petri net
    petri_net.add_transition("T1")
    petri_net.add_transition("T2")
    petri_net.add_transition("T3")
    petri_net.add_transition("T4")
    petri_net.add_transition("T5")

    # Add edges between nodes in the Petri net
    petri_net.add_edge("P1", "T1")
    petri_net.add_edge("T1", "P2")
    petri_net.add_edge("P2", "T2")
    petri_net.add_edge("T2", "P3")
    petri_net.add_edge("P3", "T3")
    petri_net.add_edge("T3", "P4")
    petri_net.add_edge("P4", "T4")
    petri_net.add_edge("T4", "P5")
    petri_net.add_edge("P2", "T5")
    petri_net.add_edge("T5", "P5")

    # Construct the reachability graph
    reachability_graph = construct_reachability_graph(petri_net)

    # Test case 1: Find paths from initial marking to {"P1": 0, "P2": 0, "P3": 1, "P4": 0, "P5": 1}
    start_marking = {"P1": 1, "P2": 0, "P3": 0, "P4": 0, "P5": 0}
    desired_marking = {"P1": 0, "P2": 0, "P3": 0, "P4": 0, "P5": 1}
    paths = find_paths(reachability_graph, start_marking, desired_marking)
    print("Paths: ", paths)
    assert len(paths) == 2
    assert paths[0] == ["T1", "T2", "T3", "T4"]
    assert paths[1] == ["T1", "T5"]

    print("\u2705 Find paths tests passed!")

    # Create a Petri net
    petri_net = PetriNet()

    # Add places to the Petri net
    petri_net.add_place("int", markings=2)
    petri_net.add_place("str", markings=0)
    petri_net.add_place("bool", markings=0)

    # Add transitions to the Petri net
    petri_net.add_transition("Multiplication")
    petri_net.add_transition("Addition")
    petri_net.add_transition("Subtraction")
    petri_net.add_transition("Concat")
    petri_net.add_transition("EqualityCheck")

    # Add edges between nodes in the Petri net
    petri_net.add_edge("int", "Multiplication", weight=2)
    petri_net.add_edge("int", "Addition", weight=2)
    petri_net.add_edge("int", "Subtraction", weight=2)
    petri_net.add_edge("Multiplication", "int", weight=1)
    petri_net.add_edge("Addition", "int", weight=1)
    petri_net.add_edge("Subtraction", "int", weight=1)
    petri_net.add_edge("str", "Concat", weight=2)
    petri_net.add_edge("Concat", "str", weight=1)
    petri_net.add_edge("int", "EqualityCheck", weight=2)
    petri_net.add_edge("EqualityCheck", "bool", weight=1)

    # Construct the reachability graph
    reachability_graph = construct_reachability_graph(petri_net)

    # Test case: Find paths from initial marking to {"int": 0, "str": 0, "bool": 1}
    start_marking = {"int": 2, "str": 0, "bool": 0}
    desired_marking = {"int": 1, "str": 0, "bool": 0}
    paths = find_paths(reachability_graph, start_marking, desired_marking)
    print("Paths: ", paths)
    assert len(paths) == 3
    assert paths == [['Multiplication'], ['Addition'], ['Subtraction']]

    program_sketches = []
    for candidate_transitions in paths:
        current_sketch = []
        for transition in candidate_transitions:
            program_sketch = generate_program_sketch(transition, 2)
            current_sketch.append(program_sketch)
        program_sketches.append(current_sketch)
    print("Program sketches: ", program_sketches)

    # Create a Petri net
    petri_net = PetriNet()

    # Add places to the Petri net
    petri_net.add_place("Shape", markings=1)
    petri_net.add_place("string", markings=0)
    petri_net.add_place("Point2D", markings=0)
    petri_net.add_place("double", markings=0)

    # Add transitions to the Petri net
    petri_net.add_transition("createTransShape")
    petri_net.add_transition("toString")
    petri_net.add_transition("createPoint2D")
    petri_net.add_transition("getX")
    petri_net.add_transition("setToRotation")

    # Add edges between nodes in the Petri net
    petri_net.add_edge("Shape", "createTransShape", weight=1)
    petri_net.add_edge("createTransShape", "Point2D", weight=1)
    petri_net.add_edge("Shape", "toString", weight=1)
    petri_net.add_edge("toString", "string", weight=1)
    petri_net.add_edge("Point2D", "createPoint2D", weight=1)
    petri_net.add_edge("createPoint2D", "Point2D", weight=1)
    petri_net.add_edge("Point2D", "getX", weight=1)
    petri_net.add_edge("getX", "double", weight=1)
    petri_net.add_edge("Shape", "setToRotation", weight=1)
    petri_net.add_edge("setToRotation", "Shape", weight=1)

    # Construct the reachability graph
    reachability_graph = construct_reachability_graph(petri_net)
    print("Edges: ", reachability_graph.edges)

    # Test case: Find paths from initial marking to {"Shape": 1, "string": 0, "Point2D": 1, "double": 0}
    start_marking = {"Shape": 1, "string": 0, "Point2D": 0, "double": 0}
    desired_marking = {"Shape": 0, "string": 0, "Point2D": 1, "double": 0}
    paths = find_paths(reachability_graph, start_marking, desired_marking)
    print("Paths: ", paths)
    assert len(paths) == 1
    assert paths == [["createTransShape"]]
    
    program_sketches = []
    for candidate_transitions in paths:
        current_sketch = []
        for transition in candidate_transitions:
            program_sketch = generate_program_sketch(transition, 1)
            current_sketch.append(program_sketch)
        program_sketches.append(current_sketch)
    print("Program sketches: ", program_sketches)

    # Create a Petri net
    petri_net = PetriNet()

    # Add places to the Petri net
    petri_net.add_place("Shape")
    petri_net.add_place("string")
    petri_net.add_place("Point2D", markings=1)
    petri_net.add_place("double", markings=1)
    petri_net.add_place("Affine Transform")
    petri_net.add_place("Area", markings=1)
    petri_net.add_place("void", markings=1)

    # Add transitions to the Petri net
    petri_net.add_transition("toString")
    petri_net.add_transition("KD")
    petri_net.add_transition("createTransShape")
    petri_net.add_transition("getX")
    petri_net.add_transition("getY")
    petri_net.add_transition("KT")
    petri_net.add_transition("KA")
    petri_net.add_transition("invert")
    petri_net.add_transition("AffineTrans")
    petri_net.add_transition("setToRotation")
    petri_net.add_transition("createTransArea")
    petri_net.add_transition("KV")

    # Add edges between nodes in the Petri net
    petri_net.add_edge("Shape", "createTransShape", weight=1)
    petri_net.add_edge("createTransShape", "Shape", weight=1)
    petri_net.add_edge("toString", "string", weight=1)
    petri_net.add_edge("Point2D", "toString", weight=1)
    petri_net.add_edge("Point2D", "KD", weight=1)
    petri_net.add_edge("KD", "Point2D", weight=2)
    petri_net.add_edge("Point2D", "getX", weight=1)
    petri_net.add_edge("Point2D", "getY", weight=1)
    petri_net.add_edge("getX", "double", weight=1)
    petri_net.add_edge("getY", "double", weight=1)
    petri_net.add_edge("Affine Transform", "createTransShape", weight=1)
    petri_net.add_edge("Affine Transform", "KT", weight=1)
    petri_net.add_edge("Affine Transform", "createTransArea", weight=1)
    petri_net.add_edge("Affine Transform", "invert", weight=1)
    petri_net.add_edge("Affine Transform", "setToRotation", weight=1)
    petri_net.add_edge("KT", "Affine Transform", weight=2)
    petri_net.add_edge("AffineTrans", "Affine Transform", weight=1)
    petri_net.add_edge("double", "setToRotation", weight=3)
    petri_net.add_edge("void", "KV", weight=1)
    petri_net.add_edge("KV", "void", weight=2)
    petri_net.add_edge("invert", "void", weight=1)
    petri_net.add_edge("setToRotation", "void", weight=1)
    petri_net.add_edge("createTransArea", "Area", weight=1)
    petri_net.add_edge("KA", "Area", weight=2)
    petri_net.add_edge("Area", "KA", weight=1)
    petri_net.add_edge("Area", "createTransArea", weight=1)

    # Identify violations. 
    k = 4  # Maximum allowed tokens in a place

    # Step 1: Identify k-safety violations
    violating_transitions = []
    for transition in petri_net.transitions:
        temp_marking = petri_net.place_markings.copy()  # Make a copy of the current marking
        updated_markings = petri_net.execute_transition(transition, temp_marking)  # Simulate firing the transition
        sum_of_markings = sum(updated_markings.values())
        if sum_of_markings > k:
            violating_transitions.append(transition)

    # Step 2: Remove violating transitions/edges
    for transition in violating_transitions:
        print("Violating transition: ", transition)

    # Construct the reachability graph
    # reachability_graph = construct_reachability_graph(petri_net)
    # pretty_print_edges(reachability_graph.edges)

    print("\u2705 Test case passed!")

def test_ant_colony_optimization():
    # Test Case 1: Simple reachability graph
    reachability_graph = ReachabilityGraph()
    reachability_graph.add_node({'A': 0, 'B': 0, 'C': 0})
    reachability_graph.add_node({'A': 1, 'B': 0, 'C': 0})
    reachability_graph.add_node({'A': 1, 'B': 1, 'C': 0})

    reachability_graph.add_edge(tuple({'A': 0, 'B': 0, 'C': 0}.items()), 'transition1', (('A', 1), ('B', 0), ('C', 0)))
    reachability_graph.add_edge(tuple({'A': 1, 'B': 0, 'C': 0}.items()), 'transition2', (('A', 1), ('B', 1), ('C', 0)))
    reachability_graph.add_edge(tuple({'A': 1, 'B': 1, 'C': 0}.items()), 'transition3', (('A', 0), ('B', 1), ('C', 0)))

    start_marking = {'A': 0, 'B': 0, 'C': 0}
    desired_marking = {'A': 1, 'B': 1, 'C': 0}
    num_ants = 5
    num_iterations = 10
    alpha = 1.0
    beta = 2.0
    evaporation_rate = 0.5

    best_path = ant_colony_optimization(reachability_graph, start_marking, desired_marking, num_ants, num_iterations, alpha, beta, evaporation_rate)
    print(f"Best path: {best_path}")  # Expected output: ['transition1', 'transition2']

# Run the test function
test_execute_transition()
test_construct_petri()
test_get_inputs()
test_get_outputs()
test_enabled_edges()
test_construct_reachability_graph()
test_find_paths()
test_ant_colony_optimization()