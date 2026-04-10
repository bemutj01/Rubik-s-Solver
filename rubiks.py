import numpy as np


class Rubiks:
    FACE_ORDER = ["Up", "Down", "Left", "Right", "Front", "Back"]

    def __init__(self, matrixList):
        def normalize_face(face):
            face_arr = np.asarray(face, dtype=object)
            if face_arr.ndim == 1 and face_arr.size == 3 and all(
                isinstance(row, (list, tuple, np.ndarray)) and len(row) == 3 for row in face_arr
            ):
                face_arr = np.vstack([np.asarray(row, dtype=object).flatten() for row in face_arr])
            elif face_arr.ndim == 1 and face_arr.size == 9:
                face_arr = face_arr.reshape((3, 3))
            if face_arr.ndim != 2 or face_arr.shape != (3, 3):
                raise ValueError("Each face must be a 3x3 matrix.")
            normalized = np.array(
                [[str(item.item()).strip() if isinstance(item, np.ndarray) and item.size == 1 else str(item).strip() for item in row] for row in face_arr],
                dtype=str,
            )
            return normalized

        if len(matrixList) == 18 and all(
            isinstance(row, (list, tuple, np.ndarray)) and len(row) == 3 for row in matrixList
        ):
            matrixList = [matrixList[i:i+3] for i in range(0, 18, 3)]
        elif len(matrixList) != 6:
            raise ValueError("Rubiks constructor requires either 6 faces or 18 rows.")

        self.faces = {
            "Up": normalize_face(matrixList[0]),
            "Down": normalize_face(matrixList[1]),
            "Left": normalize_face(matrixList[2]),
            "Right": normalize_face(matrixList[3]),
            "Front": normalize_face(matrixList[4]),
            "Back": normalize_face(matrixList[5]),
        }
        """initialize Rubiks Cube object from a list of 6 matrices, each representing a face of the cube.
        The matrices are stored in a dictionary with face names as keys for easy access. 
        The FACE_ORDER is defined for consistent ordering of faces when needed."""

    def getSideValue(self, side, x, y):
        return self.faces[side][x, y]
    """get the value of a specific bit on a face, used for checking a bit without checking the whole face."""

    def _rotate_face(self, face_name, reverse=False):
        #Rotate a face 90 degrees clockwise (or 3x if reverse)
        rotations = 3 if reverse else 1
        for _ in range(rotations):
            self.faces[face_name] = np.rot90(self.faces[face_name], k=-1)
    """rotate the face itself."""
    def isCloneOf(self, other):
        for face in self.FACE_ORDER:
            if not np.array_equal(self.faces[face], other.faces[face]):
                return False
        return True
    """check if a cube is identical to another based on face color set up."""

    def _get_left_col(self, face_name):
        #Get the left column of a face
        return self.faces[face_name][:, 0].copy()
    """get the left column of a face, used for move logic."""
    
    def _set_left_col(self, face_name, col):
        #Set the left column of a face
        self.faces[face_name][:, 0] = col
    """set the left column of a face, used for move logic."""
    
    def _get_right_col(self, face_name):
        #Get the right column of a face
        return self.faces[face_name][:, 2].copy()
    """get the right column of a face, used for move logic."""
    
    def _set_right_col(self, face_name, col):
        #Set the right column of a face
        self.faces[face_name][:, 2] = col
    """set the right column of a face, used for move logic."""
    
    def _get_top_row(self, face_name):
        #Get the top row of a face
        return self.faces[face_name][0, :].copy()
    """get the top row of a face, used for move logic."""
    
    def _set_top_row(self, face_name, row):
        #Set the top row of a face
        self.faces[face_name][0, :] = row
    """set the top row of a face, used for move logic."""

    def _get_bottom_row(self, face_name):
        #Get the bottom row of a face
        return self.faces[face_name][2, :].copy()
    """get the bottom row of a face, used for move logic."""
    def _set_bottom_row(self, face_name, row):
        #Set the bottom row of a face
        self.faces[face_name][2, :] = row
    """set the bottom row of a face, used for move logic."""
    def left(self, reverse):
        self._rotate_face("Left", reverse)
        rotations = 3 if reverse else 1
        for _ in range(rotations):
            oldUp = self._get_left_col("Up")
            oldDown = self._get_left_col("Down")
            oldFront = self._get_left_col("Front")
            oldBack = self._get_right_col("Back")
            
            self._set_left_col("Up", oldBack)
            self._set_left_col("Down", oldFront)
            self._set_left_col("Front", oldUp)
            self._set_right_col("Back", oldDown)
    """Left rotation logic. Rotate the left face, and rotate corresponding face values.
    Back face is given the opposite orientation of the left column, so right column is used for back face."""

    def right(self, reverse):
        self._rotate_face("Right", reverse)
        rotations = 3 if reverse else 1
        for _ in range(rotations):
            oldUp = self._get_right_col("Up")
            oldDown = self._get_right_col("Down")
            oldFront = self._get_right_col("Front")
            oldBack = self._get_left_col("Back")
            
            self._set_right_col("Up", oldFront)
            self._set_right_col("Down", oldBack)
            self._set_right_col("Front", oldDown)
            self._set_left_col("Back", oldUp)
    """Right rotation logic. Rotate the right face, and rotate corresponding face values.
    Back face is given the opposite orientation of the right column, so left column is used for back face."""

    def up(self, reverse):
        self._rotate_face("Up", reverse)
        rotations = 3 if reverse else 1
        for _ in range(rotations):
            oldLeft = self._get_top_row("Left")
            oldRight = self._get_top_row("Right")
            oldBack = self._get_top_row("Back")
            oldFront = self._get_top_row("Front")
            
            self._set_top_row("Left", oldFront)
            self._set_top_row("Right", oldBack)
            self._set_top_row("Front", oldRight)
            self._set_top_row("Back", oldLeft)
    """Up rotation logic. Rotate the up face, and rotate corresponding face values.
    The top rows of the left, right, back, and front faces are rotated in a cycle."""
            
    def down(self, reverse):
        self._rotate_face("Down", reverse)
        rotations = 3 if reverse else 1
        for _ in range(rotations):
            oldLeft = self._get_bottom_row("Left")
            oldRight = self._get_bottom_row("Right")
            oldBack = self._get_bottom_row("Back")
            oldFront = self._get_bottom_row("Front")
            
            self._set_bottom_row("Left", oldBack)
            self._set_bottom_row("Right", oldFront)
            self._set_bottom_row("Front", oldLeft)
            self._set_bottom_row("Back", oldRight)
        """Down rotation logic. Rotate the down face, and rotate corresponding face values.
    The bottom rows of the left, right, back, and front faces are rotated in a cycle, in the opposite direction of the up face."""

    def back(self, reverse):
        self._rotate_face("Back", reverse)
        rotations = 3 if reverse else 1
        for _ in range(rotations):
            oldLeft = self._get_left_col("Left")
            oldRight = self._get_right_col("Right")
            oldUp = self._get_top_row("Up")
            oldDown = self._get_top_row("Down")
            
            self._set_left_col("Left", oldUp)
            self._set_right_col("Right", oldDown)
            self._set_top_row("Up", oldRight)
            self._set_top_row("Down", oldLeft)
    """Back rotation logic. Rotate the back face, and rotate corresponding face values.
    The left and right columns of the left and right faces are rotated in a cycle with the top rows of the up and down faces. 
    The top rows are used for the up and down faces because the back face is oriented opposite to the front face, 
    so the top row of the up and down faces correspond to the left and right columns of the back face."""



    def front(self, reverse):
        self._rotate_face("Front", reverse)
        rotations = 3 if reverse else 1
        for _ in range(rotations):
            oldLeft = self._get_right_col("Left")
            oldRight = self._get_left_col("Right")
            oldUp = self._get_bottom_row("Up")
            oldDown = self._get_bottom_row("Down")
            
            self._set_right_col("Left", oldDown)
            self._set_left_col("Right", oldUp)
            self._set_bottom_row("Up", oldLeft)
            self._set_bottom_row("Down", oldRight)
    """Front rotation logic. Rotate the front face, and rotate corresponding face values.
    The left and right columns of the left and right faces are rotated in a cycle with the bottom rows of the up and down faces.
    The bottom rows are used for the up and down faces because the front face is oriented opposite to the back face, 
    so the bottom row of the up and down faces correspond to the left and right columns of the front face."""


    def printRubiks(self):
        for side in self.faces:
            print(side)
            print(self.faces[side])
    """Print the cube in a readable format, with each face labeled. Used for testing, debugging, and any manual code that
    wants to visualize the cube."""
    
    def getMatrix(self, side):
        return self.faces[side]
    """get the matrix of a face, used for testing and any manual code that wants to visualize the cube."""

    def isSolved(self):
        for face in self.FACE_ORDER:
            matrix = self.faces[face]
            target_color = matrix[1, 1]
            if not np.all(matrix == target_color):
                return False
        return True
    """check if the cube is solved by verifying that all stickers on each face match the center sticker of that face."""

    def clone(self):
        matrix_copy = [
            self.faces[face].copy().tolist()
            for face in self.FACE_ORDER
        ]
        return Rubiks(matrix_copy)
    """create a deep copy of the cube, used for generating new states without modifying the original cube, 
    or for convenient copying."""

    def applyMove(self, move):
        if move == "L":
            self.left(False)
        elif move == "LP":
            self.left(True)
        elif move == "R":
            self.right(False)
        elif move == "RP":
            self.right(True)
        elif move == "U":
            self.up(False)
        elif move == "UP":
            self.up(True)
        elif move == "D":
            self.down(False)
        elif move == "DP":
            self.down(True)
        elif move == "F":
            self.front(False)
        elif move == "FP":
            self.front(True)
        elif move == "B":
            self.back(False)
        elif move == "BP":
            self.back(True)
        """Move controller function. Takes a move in string format and applies the corresponding move to the cube.
        Used for any code that wants to apply moves to the cube, such as scrambling or solving logic."""  
    def manhattanDistanceFromSolved(self):
        # Simple heuristic, which counts how many bits are not in their correct place
        # For each face, the center bit determines the target color
        total_wrong = 0
        for face in self.FACE_ORDER:
            face_matrix = self.faces[face]
            target_color = face_matrix[1, 1]
            # Count bits that don't match the face color
            wrong_count = np.sum(face_matrix != target_color)
            total_wrong += wrong_count
        # Each move can fix at most 8 bits, so divide by 8 and round up
        return max(0, (total_wrong // 8) + (1 if total_wrong % 8 > 0 else 0))
"""Heuristic function to estimate the number of moves from the solved state.
    Counts how many stickers are not in the correct position, 
    and divides by 8 since each move can at most correctly position 8 stickers. Should always be admissible, 
    while still giving a reasonable estimate of distance from the solved state. Used for solving logic."""


class IDAStarNode:
    MOVES = ["L", "LP", "R", "RP", "U", "UP", "D", "DP", "F", "FP", "B", "BP"]

    def __init__(self, rubiks, path=None, parent=None):
        self.rubiks = rubiks
        self.path = path if path is not None else []
        self.parent = parent
        self.g = len(self.path)
        self.h = self.rubiks.manhattanDistanceFromSolved()
        self.f = self.g + self.h
    """Initializes values for IDAStar Node."""
    def isGoal(self):
        return self.rubiks.isSolved()
    """Checks if the node has reached the solved state."""
    def getPath(self):
        return self.path
    """Gets Path array."""
    def getRubiks(self):
        return self.rubiks
    """Gets Rubiks object."""

    def nextNodes(self):
        nodes = []
        for move in self.MOVES:
            new_rubiks = self.rubiks.clone()
            new_rubiks.applyMove(move)
            new_path = self.path + [move]
            nodes.append(IDAStarNode(new_rubiks, new_path, self))
        return nodes
    """gets the set of next nodes that can be created with moves from this point."""


class InputMatrices:
    def __init__(self, input_string):
        self.colors = input_string.split(',')
        if len(self.colors) != 54:
            raise ValueError("Input string must contain exactly 54 colors separated by commas")
    """Initializes values"""

    def makeRubiks(self):
        # Create 6 faces, each 3x3
        faces = []
        idx = 0
        for _ in range(6):
            face = []
            for _ in range(3):
                row = self.colors[idx:idx+3]
                face.append(row)
                idx += 3
            faces.append(face)
        return Rubiks(faces)
    """Converts colors to cube."""


def makeRandomRubiks(solved_cube, num_moves):
    import random
    cube = solved_cube.clone()
    moves = IDAStarNode.MOVES
    for _ in range(num_moves):
        move = random.choice(moves)
        cube.applyMove(move)
    return cube


exportedclasses = [Rubiks, IDAStarNode, InputMatrices]
exportfunctions = [makeRandomRubiks]
