import rubiks as r
import numpy as np
import argparse
import re
parser = argparse.ArgumentParser(description='Rubik\'s Cube move verifier')
parser.add_argument('cubeFile', type=str, help='Path to the input file containing cube configurations')
parser.add_argument('solutionfile', type=str, help='Path to the input file containing proposed solutions')
args = parser.parse_args()

def getMovesFromFile(filename):
    moves = []
    with open(filename, 'r') as f:
        for line in f:
            if '[' in line and ']' in line:
                move_str = line.split('[')[1].split(']')[0]
                #strip all " and ' characters from the move string.
                move_str = re.sub(r'[\'"]', '', move_str)
                move_list = move_str.split(', ')
                moves.append(move_list)
    return moves
"""Gets and shreds the move lists from the file filename. Designed to handle the formatting of the output from simulator."""

def getCubesFromFile(filename):
    cubes = []
    with open(filename, 'r') as f:
        current_cube = []
        for line in f:
            if '---------' in line:
                if current_cube:
                    InputCube = r.Rubiks(current_cube)
                    
                    cubes.append(InputCube)
                    current_cube = []
            else:
                current_cube.append([cell.strip() for cell in line.strip().split(',')])
        if current_cube:  # Add the last cube if file doesn't end with dashes
            cubes.append(current_cube)
    return cubes
"""Gets a set of data for cubes, and then appends the cubes to a list."""
            
def verifySolution():
    cubeList = getCubesFromFile(args.cubeFile)
    moveListList = getMovesFromFile(args.solutionfile)
    print(moveListList)
    for i in range(len(cubeList)):
        if cubeList[i] and moveListList[i]:  # Ensure we have both a cube and a move list for this index
            cube = cubeList[i]
            moveList = moveListList[i]
            for move in moveList:
                cube.applyMove(move)
            if cube.isSolved():
                print(f"Solution verified for cube {i} with moves: {moveList}")
            else:
                print(f"Solution not verified for cube {i}")
"""Verify solutions for the corresponding cube/List combos. 
As of current testing, movelists tend to be identical between all three settings, so this is sufficient for current testing."""

verifySolution()