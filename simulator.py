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
