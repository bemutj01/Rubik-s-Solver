import rubiks as r
import numpy as np
import time
import argparse
parser = argparse.ArgumentParser(description='Rubik\'s Cube Solver')
parser.add_argument('file', type=str, help='Path to the input file containing cube configurations')
parser.add_argument('outFile', type=str, help='Path to the output file for solutions')
args = parser.parse_args()
Rubiks = r.Rubiks
InputMatrices = r.InputMatrices
IDAStarNode = r.IDAStarNode
outFile = args.outFile
makeRandomRubiks = r.makeRandomRubiks
def IDAStar(root):
    iteration = 0
    while True:
        iteration += 1
        # print(f"Iteration {iteration}: depth_limit = {depth_limit}")
        result = IDAStarSearch(root, iteration)
        if isinstance(result, IDAStarNode):
            # print(f"Found solution in iteration {iteration}!")
            return result
        if result == float('inf'):
            return None  # No solution found
"""IDA* search implementation. 
Iteratively deepens the search by increasing the depth limit until a solution is found or all possibilities are exhausted. 
The search function checks if the current node is the goal, and if not, it generates the next nodes and continues the search recursively. 
The f value of each node is used to determine if it should be explored further based on the current depth limit."""
        
def IDAStarSearch(node, depth_limit):
    if node.isGoal():
        return node
    if node.f > depth_limit:
        return node.f
    min_threshold = float('inf')
    for next_node in node.nextNodes():
        result = IDAStarSearch(next_node, depth_limit)
        if isinstance(result, IDAStarNode):
            return result
        min_threshold = min(min_threshold, result)
    return min_threshold
"""Recursive search function for IDA*. It checks if the current node is the goal, and if not, 
it generates the next nodes and continues the search recursively.
The f value of each node is used to determine if it should be explored further based on the current depth limit. 
If a solution is found, it returns the node; if the f value exceeds the depth limit, 
it returns the f value, which is compared to other f values. 
The minimum f value that exceeds the depth limit is tracked."""


def extractCubesFromFile(filename):
    with open(filename, 'r') as f:
        cubes = []
        current_cube = []
        for line in f:
            line = line.strip()
            if line == '---------':
                if current_cube:
                    cubes.append(current_cube)
                current_cube = []
            else:
                current_cube.append(line.split(','))
        if current_cube:
            cubes.append(current_cube)  # Add the last cube if file doesn't end with separator
    return cubes
"""Function to read cube configurations from a file and convert them into a list of cube states.
The file is expected to have cube configurations separated by a line of dashes ('---------').
Each cube configuration is read as a list of rows, where each row is a list of colors.
This function is used to convert the input file into a format that can be processed to create Rubiks cube objects for solving."""

def cubesToRubiks(cubes):
    rubiks_list = []
    for cube in cubes:
        input_string = ','.join([color for row in cube for color in row])
        input_matrices = InputMatrices(input_string)
        rubiks_list.append(input_matrices.makeRubiks())
    return rubiks_list
"""Function to convert the list of cube configurations (as read from the file) into a list of Rubiks cube objects.
It takes each cube configuration, flattens it into a single string of colors, and then uses the InputMatrices class to create a Rubiks cube object from that string.
This allows for the cube configurations read from the file to be processed and solved using the IDA* algorithm implemented in the simulator."""

test_cubes = extractCubesFromFile(args.file)
rubiks_list = cubesToRubiks(test_cubes)
# successMemorizingIDAStar(IDAStarNode(rubiks_list[2]))
# print("Memorized solutions:")
# for state, path in memorized_solutions:
#    print(f"State: {state}, Path: {path}")
with open(outFile, 'w') as f:
    f.write("Results for IDA*:\n")
    for i, rubiks in enumerate(rubiks_list):
        f.write(f"Solving cube {i+1}...")
        start_time = time.time()
        solution_node = IDAStar(IDAStarNode(rubiks))
        end_time = time.time()
        if solution_node:
            f.write(f"Solution found for cube {i+1} in {end_time - start_time:.2f} seconds!")
            f.write(f"Moves: {solution_node.path}\n")
        else:
            f.write(f"No solution found for cube {i+1}.\n")
