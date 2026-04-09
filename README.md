# Rubik-s-Solver
IDA* based Rubik's Cube Solver, designed for 3x3 cube.
This code is relatively simple to run. Each code has a 2 argument execution. 

If you wish to make a randomized cube for testing, use:

python cubeMaker.py {fileName} {moveCount}

which will send a preset (currently 5) number of cubes of that movecount to your indicated file.

If you wish to find a path to solve the randomized file, use:

python simulator.py {inputFile} {outputFile}

Which will take the cube, use 3 different methods (for the sake of speed testing) and write readable outputs to an output file. P had to be substituted for ' in standard Rubiks notation, but otherwise the text should make sense.
If you wish to verify the code operated properly, use:

python verify.py {cubeFile} {moveFile}

with cubeFile being the file where the cubes tested are stored as text, and moveFile being where your output from simulator went. The code is already designed to parse these results, though it only tests the first 5, since as of current testing all results appear to match consistently. If divergences begin occuring, checking all of them may be added in a later version.