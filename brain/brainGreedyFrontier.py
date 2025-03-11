import numpy as np
from constants.moveType import MoveType
from constants.gridCellType import GridCellType

from brain.brain import Brain
from brain.brainGreedy import BrainGreedy
from brain.brainFrontier import BrainFrontier


class BrainGreedyFrontier(Brain):
    def __init__(self, agentp, brainGreedy: BrainGreedy, brainFrontier: BrainFrontier):
        self.agent = agentp
        self.brainGreedy = brainGreedy
        self.brainFrontier = brainFrontier

    # Decide what should be the next move
    # Greedy Frontier behavior thinking:
    # priority to explore partialy explored cell in vision range first
    # then looking for closest target to explore cell (Frontier)
    def thinkAndAct(self, vision, agents: list) -> MoveType:
        self.brainFrontier.updateLocalMapSize(vision)
        self.brainFrontier.gainInfoFromVision(vision)
        availableMoves = self.checkAvailableMoves(vision, agents)

        if np.any(vision == GridCellType.PARTIAL_EXPLORED.value):
            bestMove = self.brainGreedy.thinkAndAct(vision, agents)
        else:
            bestMove = self.brainFrontier.findBestMove(availableMoves)

        self.brainFrontier.updateLocalPostion(bestMove)

        # Remove current position from frontier list
        if (
            self.brainFrontier.localRow,
            self.brainFrontier.localColumn,
        ) in self.brainFrontier.localMap.frontiers:
            self.brainFrontier.localMap.removeFrontier(
                (self.brainFrontier.localRow, self.brainFrontier.localColumn)
            )

        return bestMove
