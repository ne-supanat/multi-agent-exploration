import random

from constants.moveType import MoveType
from constants.gridCellType import GridCellType

from brain.brain import Brain
from sharedMemory import SharedMemory


class BrainScout(Brain):
    def __init__(self, agentp, layoutShape, sharedMemory: SharedMemory):
        Brain.__init__(self, agentp, layoutShape)
        self.sharedMemory = sharedMemory
        self.localMap = sharedMemory.map

        self.direction = None

        self.firstContactWall = None
        self.finishedLoop = None

        self.wallHugMode = False
        self.wallHugTime = 0
        self.tol = 10

        self.zigzagHorizontalMove = MoveType.RIGHT
        self.zigzagVerticalMove = MoveType.DOWN

    # Scout behavior thinking:
    # focus on information gain (macro exploration)
    def thinkBehavior(self, vision, agents: list) -> MoveType:
        # Remove current position from frontier list
        if self.agent.getPosition() in self.sharedMemory.frontiers:
            self.sharedMemory.removeFrontier(self.agent.getPosition())

        for visionRow in range(vision.shape[0]):
            for visionColumn in range(vision.shape[1]):
                targetRow = self.agent.row + visionRow - 1
                targetColumn = self.agent.column + visionColumn - 1

                # Add new fronteir
                self.updateFrontier(
                    targetRow, targetColumn, vision[visionRow][visionColumn]
                )

        # Check if loop back to wall hugging starting point
        if self.agent.getPosition() == self.firstContactWall:
            self.finishedLoop = True

        nearWall = any(
            v == GridCellType.WALL.value
            for v in [vision[0, 1], vision[1, 0], vision[1, 2], vision[2, 1]]
        )

        # Check if any wall nearby
        if self.direction and nearWall:
            self.wallHugMode = True
            # Set wall hugging starting point if not has yet
            if not self.firstContactWall:
                self.firstContactWall = self.agent.getPosition()

        # Case: loop back to starting point or this wall already explored
        if self.finishedLoop or self.isExploredWall(vision):
            # Increase wall hug time
            self.wallHugTime += 1

            # If it exceed tolerent threshold switch to zigzag mode
            # and set new tolerent threshold (use random to prevent a patterned exploration path)
            if self.wallHugTime > self.tol:
                self.wallHugTime = 0
                self.wallHugMode = False
                self.tol = random.randint(5, 20)

        if self.wallHugMode:
            self.wallHuggerMove(vision)
        else:
            self.finishedLoop = False
            self.firstContactWall = None
            self.zigzagMove()

        return (
            self.direction if self.direction in self.availableMoves else MoveType.STAY
        )

    def isExploredWall(self, vision):
        t, l, r, b = vision[0, 1], vision[1, 0], vision[1, 2], vision[2, 1]

        return (
            (t == GridCellType.WALL.value or b == GridCellType.WALL.value)
            and l in [GridCellType.EXPLORED.value, GridCellType.WALL.value]
            and r in [GridCellType.EXPLORED.value, GridCellType.WALL.value]
        ) or (
            (l == GridCellType.WALL.value or r == GridCellType.WALL.value)
            and t in [GridCellType.EXPLORED.value, GridCellType.WALL.value]
            and b in [GridCellType.EXPLORED.value, GridCellType.WALL.value]
        )

    def wallHuggerMove(self, vision):
        # Right hand rule: make decision base on keep walls on right side of heading direction
        t, l, r, b = vision[0, 1], vision[1, 0], vision[1, 2], vision[2, 1]

        pos = [t, r, b, l]
        moves = [MoveType.UP, MoveType.RIGHT, MoveType.DOWN, MoveType.LEFT]
        size = len(pos)

        currentDirectionIndex = moves.index(self.direction)

        # If facing wrong direction
        # eg. -1: wall, 0: open, A>: agent with facing direction
        #  -1 -1 -1     -1 -1 -1
        #   0  A> 0  ->  0 <A  0
        #   0  0  0      0  0  0

        if (
            pos[(currentDirectionIndex + size + 1) % size] != GridCellType.WALL.value
            and pos[(currentDirectionIndex + size - 1) % size]
            == GridCellType.WALL.value
        ):
            currentDirectionIndex = (currentDirectionIndex + 2) % size

        if pos[currentDirectionIndex] == GridCellType.WALL.value:
            # wall front : move left (force wall to be on right side)
            self.direction = moves[(currentDirectionIndex + size - 1) % size]
            return
        if pos[(currentDirectionIndex + size + 1) % size] == GridCellType.WALL.value:
            if pos[currentDirectionIndex] == GridCellType.WALL.value:
                # wall right & front : move left
                self.direction = moves[(currentDirectionIndex + size - 1) % size]
            else:
                # wall right : move foward
                self.direction = moves[currentDirectionIndex]
        else:
            # no wall right : move right
            self.direction = moves[(currentDirectionIndex + size + 1) % size]
        return

    def zigzagMove(self):
        if self.zigzagHorizontalMove not in self.availableMoves:
            if self.zigzagHorizontalMove == MoveType.RIGHT:
                self.zigzagHorizontalMove = MoveType.LEFT
            elif self.zigzagHorizontalMove == MoveType.LEFT:
                self.zigzagHorizontalMove = MoveType.RIGHT

        if self.zigzagVerticalMove not in self.availableMoves:
            if self.zigzagVerticalMove == MoveType.UP:
                self.zigzagVerticalMove = MoveType.DOWN
            elif self.zigzagVerticalMove == MoveType.DOWN:
                self.zigzagVerticalMove = MoveType.UP

        if self.direction in [MoveType.RIGHT, MoveType.LEFT]:
            # In horizontal direction: move vertical
            self.zigzagHorizontalMove = self.direction
            self.direction = self.zigzagVerticalMove
        elif self.direction in [MoveType.UP, MoveType.DOWN]:
            # In vertical direction: move horizontal
            self.zigzagVerticalMove = self.direction
            self.direction = self.zigzagHorizontalMove
        else:
            # No direction: move horizontal
            self.direction = self.zigzagHorizontalMove

    def updateFrontier(self, row, column, value):
        if value == GridCellType.PARTIAL_EXPLORED.value and (
            not (row, column) in self.sharedMemory.frontiers
        ):
            self.sharedMemory.addFrontier((row, column))
