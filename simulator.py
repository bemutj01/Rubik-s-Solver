import rubiks as r
import numpy as np
import time
import os
import argparse
import multiprocessing
from multiprocessing import Queue, Process, cpu_count, Semaphore
from queue import Empty

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

# Storage for cube states on successful paths, stored in an array with the path following them to success.
memorized_solutions = []

def memorize_solution(cube_state, path):
    memorized_solutions.append((cube_state, path))
"""Function to store cube states and their corresponding paths to the solution. 
This is used to avoid redundant searches by checking if a cube state has already been solved during the search process.
When a solution is found, the path from the root to the solution is extracted and stored along with the cube states along that path. 
This allows for quick retrieval of solutions for previously encountered states."""

def get_memorized_solution(cube_state):
    for state, path in memorized_solutions:
        if state.isCloneOf(cube_state):
            return path
    return None
"""Function to retrieve a memorized solution for a given cube state.
It checks if the given cube state matches any of the stored states in the memorized solutions."""

def fromSolutionToMemorization(solution_node):
    current_node = solution_node
    original_path = solution_node.getPath()
    while current_node is not None:
        size = current_node.getPath().__len__()
        node_path = original_path[size:]  # Get the path from that node to the solution
        memorize_solution(current_node.getRubiks(), node_path)
        current_node = current_node.parent
"""Function to extract the path from a solution node back to the root and store the cube states along that path in the memorization storage.
This is called when a solution is found, 
and it allows for future searches to quickly retrieve solutions for previously encountered states without having to search through the entire tree again.
Will eventually have spatial limits if you wish to capture all possible solutions, 
but at that point an absurd number of iterations have already occurred, so it should not become a problem in reasonable testing."""

def successMemorizingIDAStar(root):
    iteration = 0
    while True:
        iteration += 1
        # print(f"Iteration {iteration}: depth_limit = {depth_limit}")
        result = IDAStarSearchWithMemorization(root, iteration)
        if isinstance(result, IDAStarNode):
            return result
        if result == float('inf'):
            return None  # No solution found
"""IDA* search implementation with memorization.
This version of IDA* incorporates the memorization of previously solved cube states to avoid redundant searches.
Before exploring a node, it checks if the cube state of that node has already been solved and stored in the memorization storage. 
If a solution is found for that state, it applies the moves from the current node to the solution and returns the full path to the solution.
This can significantly reduce the search time for states that have already been encountered during the search process."""

def IDAStarSearchWithMemorization(node, depth_limit):
    if node.isGoal():
        fromSolutionToMemorization(node)
        return node
    memorized_path = get_memorized_solution(node.getRubiks())
    if memorized_path is not None:
        if node.g + len(memorized_path) <= depth_limit:
            solved_rubiks = node.getRubiks().clone()
            for move in memorized_path:
                solved_rubiks.applyMove(move)
            full_path = node.getPath() + memorized_path
            return IDAStarNode(solved_rubiks, path=full_path)
    if node.f > depth_limit:
        return node.f
    min_threshold = float('inf')
    for next_node in node.nextNodes():
        result = IDAStarSearchWithMemorization(next_node, depth_limit)
        if isinstance(result, IDAStarNode):
            return result
        min_threshold = min(min_threshold, result)
    return min_threshold
"""Recursive search function for IDA* with memorization.
It checks if the current node is the goal, and if not, it first checks if the cube state of that node has already been solved and stored in the memorization storage.
If a solution is found for that state, it applies the moves from the current node to the solution and returns the full path to the solution.
If the f value of the node exceeds the depth limit, it returns the f value, which is compared to other f values. 
The minimum f value that exceeds the depth limit is tracked.
This version of the search can significantly reduce the search time for states that have already been encountered during the search process, 
as it can quickly retrieve solutions for those states without having to search through the entire tree again."""

def IDAStarWithForks(root, mem=False):
    # IDA* with process forking, capped at the number of CPU cores
    iteration = 0
    max_workers = max(cpu_count(), 16)
    while True:
        iteration += 1
        # print(f"Iteration {iteration}: depth_limit = {depth_limit}")
        if mem:
            result = IDAStarSearchWithForkedMemory(root, iteration, max_workers*4)
        else:
            result = IDAStarSearchWithForks(root, iteration, max_workers*4)
        if isinstance(result, IDAStarNode):
            return result
        if result == float('inf'):
            return None  # No solution found
"""IDA* search implementation with process forking.
This version of IDA* uses process forking to explore 
different branches of the search tree in parallel, with the number of concurrent forks capped at the number of CPU cores."""


def fork_search_worker(node, depth_limit, result_queue, mem = False):
    if(mem):
        result = IDAStarSearchWithForksRecursiveMemory(node, depth_limit)
    else:
        result = IDAStarSearchWithForksRecursive(node, depth_limit)
    result_queue.put(result)
"""Worker function that runs in a child process to perform the IDA* search."""


def IDAStarSearchWithForks(node, depth_limit, max_workers):
    if node.isGoal():
        return node
    if node.f > depth_limit:
        return node.f
    
    min_threshold = float('inf')
    next_nodes = list(node.nextNodes())
    
    if not next_nodes:
        return min_threshold
    
    # If we only have a few nodes, use direct recursion
    if len(next_nodes) <= max_workers:
        for next_node in next_nodes:
            result = IDAStarSearchWithForksRecursive(next_node, depth_limit)
            if isinstance(result, IDAStarNode):
                return result
            min_threshold = min(min_threshold, result)
        return min_threshold
    
    # For larger numbers of nodes, batch them using multiple workers
    result_queue = Queue()
    active_processes = []
    node_index = 0
    
    while node_index < len(next_nodes) or active_processes:
        # Start new processes up to max_workers limit
        while len(active_processes) < max_workers and node_index < len(next_nodes):
            next_node = next_nodes[node_index]
            p = Process(target=fork_search_worker, args=(next_node, depth_limit, result_queue))
            p.start()
            active_processes.append(p)
            node_index += 1
        
        # Collect results from any finished processes
        finished_processes = []
        for i, p in enumerate(active_processes):
            if not p.is_alive():
                # Check if this process produced a result
                try:
                    result = result_queue.get_nowait()
                    if isinstance(result, IDAStarNode):
                        # Solution found, terminate remaining processes
                        for proc in active_processes:
                            if proc.is_alive():
                                proc.terminate()
                                proc.join(timeout=1)
                        return result
                    else:
                        min_threshold = min(min_threshold, result)
                except Empty:
                    pass
                p.join()
                finished_processes.append(i)
        
        # Remove finished processes from tracking
        for i in reversed(finished_processes):
            active_processes.pop(i)
        
        # If no processes finished yet, wait a bit to avoid busy waiting
        if finished_processes or len(active_processes) < max_workers:
            time.sleep(0.001)
    
    return min_threshold
"""
Parallel IDA* search function that uses process forking with bounded concurrency.
Limits the number of concurrent child processes to the number of CPU cores.
Each child process explores a different branch of the search tree.
"""


def IDAStarSearchWithForksRecursive(node, depth_limit):
    """
    Recursive search function for IDA* with forking.
    This is the actual recursive search that runs in both parent and child processes.
    """
    if node.isGoal():
        return node
    if node.f > depth_limit:
        return node.f
    
    min_threshold = float('inf')
    for next_node in node.nextNodes():
        result = IDAStarSearchWithForksRecursive(next_node, depth_limit)
        if isinstance(result, IDAStarNode):
            return result
        min_threshold = min(min_threshold, result)
    return min_threshold
"""
Recursive search function for IDA* with forking.
This performs the standard recursive IDA* search without additional forking at this level.
"""

def IDAStarSearchWithForkedMemory(node, depth_limit, max_workers):
    if node.isGoal():
        fromSolutionToMemorization(node)
        return node
    memorized_path = get_memorized_solution(node.getRubiks())
    if memorized_path is not None:
        if node.g + len(memorized_path) <= depth_limit:
            solved_rubiks = node.getRubiks().clone()
            for move in memorized_path:
                solved_rubiks.applyMove(move)
            full_path = node.getPath() + memorized_path
            return IDAStarNode(solved_rubiks, path=full_path)
    if node.f > depth_limit:
        return node.f
    
    min_threshold = float('inf')
    next_nodes = list(node.nextNodes())
    
    if not next_nodes:
        return min_threshold
    
    # If we only have a few nodes, use direct recursion
    if len(next_nodes) <= max_workers:
        for next_node in next_nodes:
            result = IDAStarSearchWithForksRecursiveMemory(next_node, depth_limit)
            if isinstance(result, IDAStarNode):
                return result
            min_threshold = min(min_threshold, result)
        return min_threshold
    
    # For larger numbers of nodes, batch them using multiple workers
    result_queue = Queue()
    active_processes = []
    node_index = 0
    
    while node_index < len(next_nodes) or active_processes:
        # Start new processes up to max_workers limit
        while len(active_processes) < max_workers and node_index < len(next_nodes):
            next_node = next_nodes[node_index]
            p = Process(target=fork_search_worker, args=(next_node, depth_limit, result_queue, True))
            p.start()
            active_processes.append(p)
            node_index += 1
        
        # Collect results from any finished processes
        finished_processes = []
        for i, p in enumerate(active_processes):
            if not p.is_alive():
                # Check if this process produced a result
                try:
                    result = result_queue.get_nowait()
                    if isinstance(result, IDAStarNode):
                        # Solution found, terminate remaining processes
                        for proc in active_processes:
                            if proc.is_alive():
                                proc.terminate()
                                proc.join(timeout=1)
                        return result
                    else:
                        min_threshold = min(min_threshold, result)
                except Empty:
                    pass
                p.join()
                finished_processes.append(i)
        
        # Remove finished processes from tracking
        for i in reversed(finished_processes):
            active_processes.pop(i)
        
        # If no processes finished yet, wait a bit to avoid busy waiting
        if finished_processes or len(active_processes) < max_workers:
            time.sleep(0.001)
    
    return min_threshold
"""Forked search function but with added memory checking system."""


def IDAStarSearchWithForksRecursiveMemory(node, depth_limit):
    """
    Recursive search function for IDA* with forking.
    This is the actual recursive search that runs in both parent and child processes.
    """
    if node.isGoal():
        fromSolutionToMemorization(node)
        return node
    memorized_path = get_memorized_solution(node.getRubiks())
    if memorized_path is not None:
        if node.g + len(memorized_path) <= depth_limit:
            solved_rubiks = node.getRubiks().clone()
            for move in memorized_path:
                solved_rubiks.applyMove(move)
            full_path = node.getPath() + memorized_path
            return IDAStarNode(solved_rubiks, path=full_path)
    if node.f > depth_limit:
        return node.f
    
    min_threshold = float('inf')
    for next_node in node.nextNodes():
        result = IDAStarSearchWithForksRecursiveMemory(next_node, depth_limit)
        if isinstance(result, IDAStarNode):
            return result
        min_threshold = min(min_threshold, result)
    return min_threshold
"""
Recursive search function for IDA* with forking.
This performs the standard recursive IDA* search without additional forking at this level.
"""

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
    totalSolve = [0,0,0,0,0,0]
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
        totalSolve[0] += end_time - start_time

    for i, rubiks in enumerate(rubiks_list):
        f.write(f"Solving cube using forking {i+1}...")
        start_time = time.time()
        solution_node = IDAStarWithForks(IDAStarNode(rubiks))
        end_time = time.time()
        if solution_node:
            f.write(f"Solution found for cube {i+1} in {end_time - start_time:.2f} seconds!")
            f.write(f"Moves: {solution_node.path}\n")
        else:
            f.write(f"No solution found for cube {i+1}.\n")
        totalSolve[1] += end_time - start_time
    for i, rubiks in enumerate(rubiks_list):
        f.write(f"Solving cube {i+1} with memorization...")
        start_time = time.time()
        solution_node = successMemorizingIDAStar(IDAStarNode(rubiks))
        end_time = time.time()
        if solution_node:
            f.write(f"Solution found for cube {i+1} in {end_time - start_time:.2f} seconds!")
            f.write(f"Moves: {solution_node.path}\n"    )
        else:
            f.write(f"No solution found for cube {i+1}.\n")
        totalSolve[2] += end_time - start_time

    for i, rubiks in enumerate(rubiks_list):
        f.write(f"Solving cube {i+1} again with memorization...")
        start_time = time.time()
        solution_node = successMemorizingIDAStar(IDAStarNode(rubiks))
        end_time = time.time()
        if solution_node:
            f.write(f"Solution found for cube {i+1} in {end_time - start_time:.2f} seconds!")
            f.write(f"Moves: {solution_node.path}\n"    )
        else:
            f.write(f"No solution found for cube {i+1}.\n")
        totalSolve[3] += end_time - start_time
    memorized_solutions = []
    for i, rubiks in enumerate(rubiks_list):
        f.write(f"Solving cube {i+1} with memorization and Forks...")
        start_time = time.time()
        solution_node = IDAStarWithForks(IDAStarNode(rubiks), True)
        end_time = time.time()
        if solution_node:
            f.write(f"Solution found for cube {i+1} in {end_time - start_time:.2f} seconds!")
            f.write(f"Moves: {solution_node.path}\n"    )
        else:
            f.write(f"No solution found for cube {i+1}.\n")
        totalSolve[4] += end_time - start_time

    for i, rubiks in enumerate(rubiks_list):
        f.write(f"Solving cube {i+1} again with memorization and Forks...")
        start_time = time.time()
        solution_node = IDAStarWithForks(IDAStarNode(rubiks), True)
        end_time = time.time()
        if solution_node:
            f.write(f"Solution found for cube {i+1} in {end_time - start_time:.2f} seconds!")
            f.write(f"Moves: {solution_node.path}\n"    )
        else:
            f.write(f"No solution found for cube {i+1}.\n")
        totalSolve[5] += end_time - start_time
    f.write(f"Total runtime for base IDA: {totalSolve[0]}\n")
    f.write(f"Total runtime for Forked IDA: {totalSolve[1]}\n")
    f.write(f"Total runtime for base Memory IDA: {totalSolve[2]}\n")
    f.write(f"Total runtime for Memory IDA with pre-found solutions: {totalSolve[3]}\n")
    f.write(f"Total runtime for Forked Memory IDA: {totalSolve[4]}\n")
    f.write(f"Total runtime for Forked Memory IDA with pre-found solutions: {totalSolve[5]}\n")
    
"""This block of code reads the cube configurations from the input file, converts them into Rubiks cube objects, 
and then applies both the standard IDA* search and the memorization-enhanced IDA* search to solve each cube for testing purposes.
The results, including the time taken and the moves to solve each cube, are written to the specified output file.
This allows for a comparison of the performance of the two search methods on the same set of cube configurations, 
demonstrating the potential benefits of memorization in reducing search time for previously encountered states, 
but also the drawbacks of initially slower execution times."""
    