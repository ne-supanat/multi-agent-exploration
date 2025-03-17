from constants.moveType import MoveType
from constants.gridCellType import GridCellType

from brain.brain import Brain
from sharedMemory import SharedMemory

from aStar import aStarSearch


class BrainFrontier(Brain):
    def __init__(self, agentp, layoutShape, sharedMemory: SharedMemory):
        Brain.__init__(self, agentp, layoutShape)
        self.sharedMemory = sharedMemory
        self.localMap = sharedMemory.map
        self.targetCell = None
        self.queue = []
        self.stuck = 0

    # Frontier behavior thinking:
    # remember discovered frontier cells
    def thinkBehavior(self, vision, agents: list) -> MoveType:
        # Reach target cell
        if self.agent.getPosition() == self.targetCell:
            self.sharedMemory.completeTask(self.agent.name)
            self.targetCell = None

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

        bestMove = self.findBestMove()

        return bestMove

    def findBestMove(self):
        # Recall & check self target cell with blackboard
        if self.agent.name in self.sharedMemory.blackboard:
            self.targetCell = self.sharedMemory.blackboard[self.agent.name]

        # Find new target cell
        # if currently not have one
        if self.targetCell == None:
            self.findNewTargetCell()

        # if stuck for too long (3 turns) give up on task
        if self.targetCell and self.stuck > 2:
            self.stuck = 0
            self.sharedMemory.giveUpOnTask(self.agent.name)
            return self.findBestMove()

        # Planing path for new target or if stuck try find new path
        if not self.queue or self.stuck > 0:
            self.planNewPath()

        if self.queue:
            # Move following sequence in queue if possible
            if self.queue[0] in self.availableMoves:
                bestMove = self.queue.pop(0)
            else:
                # If not movable then update stuck count
                self.stuck += 1
                bestMove = MoveType.STAY
        else:
            bestMove = MoveType.STAY

        return bestMove

    def updateFrontier(self, row, column, value):
        if value == GridCellType.PARTIAL_EXPLORED.value and (
            not (row, column) in self.sharedMemory.frontiers
        ):
            self.sharedMemory.addFrontier((row, column))

    def findNewTargetCell(self):
        # Find the closest cell from frontier list
        if len(self.sharedMemory.frontiers) > 0:
            closestFrontier = None
            closestDistance = float("inf")

            for frontier in self.sharedMemory.frontiers:
                fronteirRow, fronteirColumn = frontier

                distance = abs(fronteirRow - self.agent.row) + abs(
                    fronteirColumn - self.agent.column
                )

                if distance < closestDistance:
                    closestDistance = distance
                    closestFrontier = frontier

            self.targetCell = closestFrontier
            self.planNewPath()

            # Update blackboard
            # remove target frontier from other agent
            for agentName in self.sharedMemory.blackboard:
                if self.targetCell == self.sharedMemory.blackboard[agentName]:
                    self.sharedMemory.giveUpOnTask(agentName)

            # update blackboard with target frontier on agent name
            self.sharedMemory.signUpOnTask(self.agent.name, self.targetCell)

    def planNewPath(self):
        self.queue.clear()

        # If no place assigned then stay
        if self.targetCell is None:
            self.queue.append(MoveType.STAY)
            return

        # Search best path using A* algorithm
        # path is in format of [(row, column), ...]
        path = aStarSearch(
            self.localMap, (self.agent.row, self.agent.column), self.targetCell
        )

        # Finding path fail then wait
        if path is None:
            self.queue.append(MoveType.STAY)
            return

        # Create sequence of movement following path from A*
        for i in range(len(path) - 1):
            pCurrent = path[i]
            pNext = path[i + 1]

            pCurrentRow, pCurrentColumn = pCurrent
            pNextRow, pNextColumn = pNext

            if pCurrentRow > pNextRow:
                self.queue.append(MoveType.UP)
            if pCurrentRow < pNextRow:
                self.queue.append(MoveType.DOWN)
            if pCurrentColumn > pNextColumn:
                self.queue.append(MoveType.LEFT)
            if pCurrentColumn < pNextColumn:
                self.queue.append(MoveType.RIGHT)
