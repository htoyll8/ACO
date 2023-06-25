import inspect
from collections import deque

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
                raise ValueError(f"Not enough tokens in place {input_place} to fire transition {transition}.")

        # 
        output_place = next(iter(self.edges[transition].keys()))

        # Consume tokens from input places
        for input_place in inputs:
            edge_weight = self.edges[input_place][transition]
            # Add tokens to the output place
            updated_place_markings[output_place] += updated_place_markings[input_place]
            updated_place_markings[input_place] -= edge_weight
        
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

    while worklist:
        current_markings = worklist.popleft()
        current_markings_tuple = tuple(current_markings.items())
        reachability_graph.add_node(current_markings)

        enabled_transitions = petri_net.enabled_edges(current_markings)
        for transition in enabled_transitions:
            successor_markings = petri_net.execute_transition(transition, current_markings)
            successor_markings_tuple = tuple(successor_markings.items())

            reachability_graph.add_node(successor_markings)
            reachability_graph.add_edge(current_markings_tuple, transition, successor_markings_tuple)

            worklist.append(successor_markings)

    return reachability_graph

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

    # Check the updated markings
    expected_markings = {"P1": 0, "P2": 3, "P3": 0}

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
    expected_markings = {"P1": 0, "P2": 4, "P3": 0}

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

# Run the test function
test_execute_transition()
test_construct_petri()
test_get_inputs()
test_get_outputs()
test_enabled_edges()
test_construct_reachability_graph()
