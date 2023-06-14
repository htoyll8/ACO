import inspect

class PetriNet:
    def __init__(self):
        """
        Initializes an empty Petri net.
        """
        self.places = {}  # Dictionary to store places and their token counts
        self.transitions = {}  # Dictionary to store transitions and their input places
        self.edges = {}  # Dictionary to store edge weights between places and transitions

    def add_place(self, place):
        """
        Adds a place to the Petri net.

        Args:
            place (str): Name of the place.
        """
        self.places[place] = 0  # Initializes the token count of the place to 0

    def add_transition(self, transition):
        """
        Adds a transition to the Petri net.

        Args:
            transition (str): Name of the transition.
        """
        self.transitions[transition] = {}  # Initializes an empty dictionary to store input places for the transition

    def add_edge(self, place, transition, weight=1):
        """
        Adds an edge between a place and a transition in the Petri net.

        Args:
            place (str): Name of the input place.
            transition (str): Name of the transition.
            weight (int): Weight of the edge (default is 1).
        """
        if place not in self.places or transition not in self.transitions:
            raise ValueError("Invalid place or transition")  # Error handling for invalid place or transition
        
        self.transitions[transition][place] = weight  # Sets the weight of the edge from place to transition

    def execute_transition(self, transition):
        """
        Executes a transition in the Petri net by consuming tokens from input places.

        Args:
            transition (str): Name of the transition.
        """
        for place, weight in self.transitions[transition].items():
            self.places[place] -= weight  # Decrements the token count of each input place based on the edge weight

    def get_marking(self):
        """
        Retrieves the current marking (token counts) of all places in the Petri net.

        Returns:
            dict: A dictionary mapping place names to their token counts.
        """
        return self.places.copy()  # Returns a copy of the dictionary containing the place names and token counts

def construct_petri(components):
    """
    Constructs a Petri net based on the given components.

    Args:
        components (list): List of components.

    Returns:
        PetriNet: Constructed Petri net.
    """
    petri_net = PetriNet()  # Create an empty Petri net

    for component in components:
        inputs = get_inputs(component)  # Get the input types for the component
        output = get_output(component)  # Get the output type for the component

        for input_type in inputs:
            petri_net.add_place(input_type)  # Add a place for each input type
            petri_net.add_edge(input_type, component, weight=len(inputs[input_type]))  # Add an edge from the input type to the component

        petri_net.add_transition(component)  # Add a transition for the component
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
        
        # Add the parameter to the corresponding input type
        if input_type in inputs:
            inputs[input_type].append(parameter.name)
        else:
            inputs[input_type] = [parameter.name]
    
    return inputs
