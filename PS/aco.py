import random

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

    def __str__(self):
        return str(self.value)

class BinOp(Node):
    def __init__(self, value):
        super().__init__(value)
        self.num_children = 2

class Addition(BinOp):
    def __init__(self):
        super().__init__('+')

class Subtraction(BinOp):
    def __init__(self):
        super().__init__('-')

class Multiplication(BinOp):
    def __init__(self):
        super().__init__('*')

class Ant:
    def generate_ast(self, pheromones):
        operator = self.select_operator(pheromones)
        node = Node(operator.value)
        for _ in range(operator.num_children):
            child = self.select_constant(pheromones)
            node.children.append(child)
        return node

    def select_operator(self, pheromones):
        operators = [Addition(), Subtraction(), Multiplication()]
        pheromone_levels = [pheromones[op.value] for op in operators]
        total_pheromones = sum(pheromone_levels)
        probabilities = [p / total_pheromones for p in pheromone_levels]
        return random.choices(operators, probabilities)[0]

    def select_constant(self, pheromones):
        constants = [1, 2, 3, 4, 5]
        pheromone_levels = [pheromones[str(c)] for c in constants]
        total_pheromones = sum(pheromone_levels)
        probabilities = [p / total_pheromones for p in pheromone_levels]
        selected_constant = random.choices(constants, probabilities)[0]
        return Node(selected_constant)
    
class Synthesizer:
    def __init__(self, ants, expected_result, iterations):
        self.ants = ants
        self.iterations = iterations
        self.expected_result = expected_result
        self.programs_fitness = []  # Instance variable to store programs and their fitness scores
        self.top_solutions = []
        self.pheromones = {
            '+': 1.0,  # Initial pheromone level for addition
            '-': 1.0,  # Initial pheromone level for subtraction
            '*': 1.0,  # Initial pheromone level for multiplication
            '1' : 1.0,
            '2' : 1.0,
            '3' : 1.0,
            '4' : 1.0,
            '5' : 1.0
        }

    def run(self):
        for _ in range(self.iterations):
            for ant in self.ants:
                ast = ant.generate_ast(self.pheromones)
                result = evaluate_program(ast)
                fitness_score = 1.0 / (abs(result - self.expected_result) + 1)  # Calculate fitness score based on the difference from the expected value, adding 1 to avoid division by zero
                program_tuple = (ast, fitness_score)
                if not self.is_duplicate_program(program_tuple):
                    self.programs_fitness.append(program_tuple)  # Store the program and its fitness score

            # Sort the programs by fitness score in descending order
            self.programs_fitness.sort(key=lambda x: x[1], reverse=True)
            print("Fitnesses: ", self.programs_fitness)

            # Update the top solutions with the current best programs
            self.top_solutions = [program for program, _ in self.programs_fitness[:10]]

            # Update the pheromone levels based on the fitness score
            self.update_pheromones(self.programs_fitness)

    def update_pheromones(self, programs_fitness):
        for program, fitness_score in programs_fitness:
            if program.children:
                self.pheromones[program.value] += fitness_score
                for child in program.children:
                    self.pheromones[str(child.value)] += fitness_score
    
    def is_duplicate_program(self, program_tuple):
        ast, _ = program_tuple
        for existing_ast, _ in self.programs_fitness:
            if self.are_programs_equal(ast, existing_ast):
                return True
        return False

    def are_programs_equal(self, ast1, ast2):
        if ast1.value != ast2.value:
            return False
        if len(ast1.children) != len(ast2.children):
            return False
        for child1, child2 in zip(ast1.children, ast2.children):
            if not self.are_programs_equal(child1, child2):
                return False
        return True

# Function to print the program in tree format
def print_program(node):
    if node.children:
        print(f'({node} ', end='')
        for child in node.children:
            print_program(child)
        print(')', end='')
    else:
        print(f'{node} ', end='')

# Function to evaluate the program
def evaluate_program(node):
    if isinstance(node, Node):
        if node.children:
            operator = node.value
            operands = [evaluate_program(child) for child in node.children]
            if operator == '+':
                print("Add!")
                return sum(operands)
            elif operator == '-':
                print("Sub!")
                return operands[0] - sum(operands[1:])
            elif operator == '*':
                print("Mul!")
                result = 1
                for operand in operands:
                    result *= operand
                return result
        else:
            return node.value

# Example usage
ant1 = Ant()
ant2 = Ant()
ant3 = Ant()

synthesizer = Synthesizer([ant1, ant2, ant3], 4, iterations=100)
synthesizer.run()

for program in synthesizer.top_solutions:
    print_program(program)