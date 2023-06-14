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
