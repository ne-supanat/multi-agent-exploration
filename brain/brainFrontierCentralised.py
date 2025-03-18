from constants.moveType import MoveType
from constants.gridCellType import GridCellType

from brain.brain import Brain
from sharedMemory import SharedMemory
from brain.centralNode import CentralNode

from aStar import aStarSearch

from constants.moveType import MoveType
from constants.gridCellType import GridCellType

from brain.brainFrontier import BrainFrontier
from sharedMemory import SharedMemory

from aStar import aStarSearch


class BrainFrontierCentralised(BrainFrontier):
    def __init__(
        self, agentp, layoutShape, sharedMemory: SharedMemory, centralNode: CentralNode
    ):
        BrainFrontier.__init__(self, agentp, layoutShape, sharedMemory)
        self.centralNode = centralNode

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

        # Use first move to gather information for centralised path planing
        if not self.centralNode.initialised:
            self.centralNode.gatheringInfo(self.agent)
            return MoveType.STAY

        bestMove = self.findBestMove()

        return bestMove

    def findNewTargetCell(self):
        # Request new target
        self.targetCell = self.centralNode.getNextTarget(self.agent)
        self.planNewPath()

        # Update blackboard
        # remove target frontier from other agent
        for agentName in self.sharedMemory.blackboard:
            if self.targetCell == self.sharedMemory.blackboard[agentName]:
                self.sharedMemory.giveUpOnTask(agentName)

        # update blackboard with target frontier on agent name
        self.sharedMemory.signUpOnTask(self.agent.name, self.targetCell)
