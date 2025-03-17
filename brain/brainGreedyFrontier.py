import numpy as np
from constants.moveType import MoveType
from constants.gridCellType import GridCellType

from brain.brain import Brain
from brain.brainGreedy import BrainGreedy
from brain.brainFrontier import BrainFrontier


class BrainGreedyFrontier(Brain):
    def __init__(
        self,
        agentp,
        layoutShape,
        brainGreedy: BrainGreedy,
        brainFrontier: BrainFrontier,
    ):
        Brain.__init__(self, agentp, layoutShape)
        self.agent = agentp
        self.brainGreedy = brainGreedy
        self.brainFrontier = brainFrontier

    # Decide what should be the next move
    # Greedy Frontier behavior thinking:
    # priority to explore partialy explored cell in vision range first
    # then looking for closest target to explore cell (Frontier)
    def thinkBehavior(self, vision, agents: list) -> MoveType:
        self.brainFrontier.localMap = self.localMap
        self.brainFrontier.visitedMap = self.visitedMap
        self.brainFrontier.availableMoves = self.availableMoves

        # Reach target cell
        if self.agent.getPosition() == self.brainFrontier.targetCell:
            self.brainFrontier.sharedMemory.completeTask(self.agent.name)
            self.targetCell = None

        # Remove current position from frontier list
        if self.agent.getPosition() in self.brainFrontier.sharedMemory.frontiers:
            self.brainFrontier.sharedMemory.removeFrontier(self.agent.getPosition())

        for visionRow in range(vision.shape[0]):
            for visionColumn in range(vision.shape[1]):
                targetRow = self.agent.row + visionRow - 1
                targetColumn = self.agent.column + visionColumn - 1

                # Add new fronteir
                self.brainFrontier.updateFrontier(
                    targetRow, targetColumn, vision[visionRow][visionColumn]
                )

        if np.any(vision == GridCellType.PARTIAL_EXPLORED.value):
            bestMove = self.brainGreedy.thinkAndAct(vision, agents)
        else:
            bestMove = self.brainFrontier.findBestMove()

        return bestMove

    # def thinkAndAct(self, vision, agents: list) -> MoveType:
    #     self.brainFrontier.gainInfoFromVision(vision)
    #     availableMoves = self.checkAvailableMoves(vision, agents)

    #     if np.any(vision == GridCellType.PARTIAL_EXPLORED.value):
    #         bestMove = self.brainGreedy.thinkAndAct(vision, agents)
    #     else:
    #         bestMove = self.brainFrontier.findBestMove(availableMoves)

    #     return bestMove
