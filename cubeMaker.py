import rubiks as r
import numpy as np
import argparse
parser = argparse.ArgumentParser(description='Rubik\'s Cube Solver')
parser.add_argument('file', type=str, help='Path to the input file for cube configurations')
parser.add_argument('--moveCount', type=int, default=7, help='Number of random moves to apply to the cube')
parser.add_argument('--cubeCount', type=int, default=5, help='Number of cubes to build in the file.')
args = parser.parse_args()
Rubiks = r.Rubiks
InputMatrices = r.InputMatrices
makeRandomRubiks = r.makeRandomRubiks

def sendRubiksToFile(rubiks, filename):
    with open(filename, 'w') as f:
        for cubes in rubiks:
            for face in cubes.faces:
                face_matrix = cubes.faces[face]
                for row in face_matrix:
                    f.write(','.join(map(str, row)) + '\n')
            f.write('---------\n')  # Separate different cubes with a blank line        
"""function to send the generated cubes to a file, with each cube separated by a blank line with dashes 
to make it easier to separate cubes when converting back to cube objects."""

colors = "WRBOGY"
fullSquare = ",".join([color for color in colors for _ in range(9)])
inputMatrices = InputMatrices(fullSquare)
rubiksToFile = [makeRandomRubiks(inputMatrices.makeRubiks(), num_moves=args.moveCount) for _ in range(args.cubeCount)]
sendRubiksToFile(rubiksToFile, args.file)
"""Generation logic. Currently makes 5, may make version with for instead of manual loop once larger scale compute is available for solving.
Cubes are given a number of random moves such that one can easily generate cubes for testing."""
