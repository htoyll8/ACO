import inspect

class PetriNet:
    def __init__(self):
        """
        Initializes an empty Petri net.
        """
        self.places = set()  # Set to store places
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

    def execute_transition(self, transition):
        """
        Executes a transition in the Petri net.

        Args:
            transition (str): Name of the transition.
        """
        edge_weight = list(self.edges[transition].values())[0]  # Access the first value of the dictionary
        transition_output_place = list(self.edges[transition].keys())[0]  # Access the first key of the dictionary
        self.place_markings[transition_output_place] += edge_weight

        for node1, output_dict in self.edges.items():
            if node1 in self.places and transition in output_dict.keys():
                edge_weight = output_dict[transition]
                self.place_markings[node1] -= edge_weight

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
    parameters = signature.parameters.values()

    for component in components:
        inputs = get_inputs(component)  # Get the input types for the component
        output = get_outputs(component)  # Get the output type for the component

        petri_net.add_transition(component)  # Add a transition for the component

        for input_type in inputs:
            if input_type not in petri_net.places:
                petri_net.add_place(input_type)  # Add the place if it doesn't exist already

            if any(param.annotation == input_type for param in parameters):
                count = sum(1 for param in parameters if param.annotation == input_type)
                petri_net.places[input_type] += count  # Increment the token count of the place by the count

            petri_net.add_edge(input_type, component, weight=len(inputs[input_type]))  # Add an edge from the input type to the component

        if output not in petri_net.places:
            petri_net.add_place(output)  # Add the place for the output type if it doesn't exist already

        print("Look: ", petri_net.places, petri_net.transitions)
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
        The output type of the component, or None if not found.
    """
    output_type = None

    # Check if the component is a function or method
    if inspect.isfunction(component) or inspect.ismethod(component):
        signature = inspect.signature(component)
        return_type = signature.return_annotation
        if return_type != inspect.Signature.empty:
            output_type = return_type

    return output_type

# Test cases

def test_petri_net():
    petri_net = PetriNet()

    # Add places
    petri_net.add_place("P1", markings=1)
    petri_net.add_place("P2")
    petri_net.add_place("P3", markings=2)

    # Add transitions
    petri_net.add_transition("T1")
    petri_net.add_transition("T2")
    petri_net.add_transition("T3")

    # Add edges between transitions and places
    petri_net.add_edge("P1", "T1", weight=1)
    petri_net.add_edge("T1", "P2", weight=1)
    petri_net.add_edge("P2", "T2", weight=2)
    petri_net.add_edge("T2", "P3", weight=1)
    petri_net.add_edge("P3", "T3", weight=1)

    # Execute a transition
    petri_net.execute_transition("T1")

    # Check the updated markings
    assert petri_net.get_markings() == {"P1": 0, "P2": 1, "P3": 2}

    # Execute another transition
    petri_net.execute_transition("T2")

    # Check the updated markings
    assert petri_net.get_markings() == {"P1": 0, "P2": -1, "P3": 3}

    print("Petri net tests passed!")

def test_construct_petri():
    def example_function(x: int, y: str, z: float) -> int:
        pass

    components = [example_function]  # Example list of components
    
    petri_net = construct_petri(components, example_function)
    
    # Verify the places and their initial markings
    expected_marking = {
        int: 1,
        str: 1,
        float: 1,
        None.__class__: 1
    }
    assert petri_net.get_markings() == expected_marking
    
    print("Construct petri net tests passed!")

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

    print("Get inputs tests passed!")

def test_get_outputs():
    def add(a: int, b: int) -> int:
        return a + b

    def multiply(a: float, b: float) -> float:
        return a * b

    def no_return_type(a: str):
        return len(a)

    assert get_outputs(add) == int
    assert get_outputs(multiply) == float
    assert get_outputs(no_return_type) is None

    print("Get outputs tests passed!")


# Run the test function
test_petri_net()
# test_construct_petri()
test_get_inputs()
test_get_outputs()
