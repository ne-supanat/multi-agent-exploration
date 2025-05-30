import random

from constants.moveType import MoveType
from constants.gridCellType import GridCellType

from brain.centralNode import CentralNode
from brain.centralNodeZoneSplit import CentralNodeZoneSplit
from brain.centralNodeZoneVoronoi import CentralNodeZoneVoronoi
from brain.brain import Brain

from aStar import aStarSearch


class BrainZoneSplit(Brain):
    def __init__(self, agentp, layoutShape, centralNode: CentralNode):
        Brain.__init__(self, agentp, layoutShape)
        self.centralNode = centralNode
        self.localMap = centralNode.sharedMemory.map
        self.targetCell = None
        self.queue = []
        self.stuck = 0
        self.invalidTarget = []
        self.planingFail = 0

    # Zone centralised behavior thinking:
    # explore the zone assigned by central node
    def thinkBehavior(self, vision, agents: list) -> MoveType:
        # Request central node to recheck and update target queue
        # eg. some of target might be wall or already explored
        if type(self.centralNode) == CentralNodeZoneSplit:
            self.centralNode.recheckTargetCells(self.agent)
        if type(self.centralNode) == CentralNodeZoneVoronoi:
            self.centralNode.recheckTargetQueues(self.agent)

        bestMove = self.findBestMove(agents)

        return bestMove

    def findBestMove(self, agents):
        # Reset target cell if it is wall or already got explored
        if self.targetCell and (
            (self.targetCell == self.agent.getPosition())
            or (
                self.localMap[self.targetCell[0], self.targetCell[1]]
                in [GridCellType.WALL.value, GridCellType.EXPLORED.value]
            )
        ):
            self.targetCell = None

        # Find new target cell
        # if currently not have one
        if self.targetCell == None:
            self.findNewTargetCell(agents)

        # if stuck for too long (9 turns) do a random move
        if self.planingFail > 2:
            self.planingFail = 0
            return random.choice(list(self.availableMoves))

        # if stuck for too long (3 turns) request new target/ delay current target
        if self.targetCell and self.stuck > 2:
            self.stuck = 0
            self.planingFail += 1
            if type(self.centralNode) is CentralNodeZoneVoronoi:
                self.centralNode.planAll()
            self.targetCell = None
            return self.findBestMove(agents)

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

    def findNewTargetCell(self, otherAgents):
        # Request new target
        self.targetCell = self.centralNode.getNextTarget(self.agent)
        if self.targetCell:
            self.planNewPath()
        elif type(self.centralNode) is CentralNodeZoneVoronoi:
            # Voronoi; Agent completed assigned area: trying to find new zone to explore

            # Moving toward other agents, avoiding stuck in same area
            # create a better zone partitioning
            sumRow = 0
            sumColumn = 0

            for agent in otherAgents:
                sumRow += agent.row
                sumColumn += agent.column

            centerPointRow = sumRow // len(otherAgents)
            centerPointColumn = sumColumn // len(otherAgents)

            self.targetCell = centerPointRow, centerPointColumn

            # Request for re-planning zone
            self.centralNode.planAll()

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

        # Finding path fail then wait and put that target to unreachable cells list
        if path is None:
            if type(self.centralNode) == CentralNodeZoneSplit:
                self.centralNode.addBlockedCells(self.agent, self.targetCell)
            self.targetCell = None
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
