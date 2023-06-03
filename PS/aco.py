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

def generate_ast(depth):
    if depth == 0:
        return random.choice([Addition(), Subtraction(), Multiplication()])
    else:
        node = random.choice([Addition(), Subtraction(), Multiplication()])
        for _ in range(node.num_children):
            if random.random() < 0.5:  # Generate a constant (leaf node)
                child = Node(random.randint(1, 5))
            else:  # Generate another operator (binop node)
                child = generate_ast(depth - 1)
            node.children.append(child)
        return node

def print_program(node):
    if node.children:
        print(f'({node} ', end='')
        for child in node.children:
            print_program(child)
        print(')', end='')
    else:
        print(f'{node} ', end='')

depth = 3
ast = generate_ast(depth)
print_program(ast)
