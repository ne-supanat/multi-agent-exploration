import random
import numpy as np

from constants.moveType import MoveType
from constants.gridCellType import GridCellType

from brain.brain import Brain


class BrainGreedy(Brain):
    # Decide what should be the next move
    def thinkAndAct(self, vision, agents: list) -> MoveType:
        availableMoves = self.checkAvailableMoves(vision, agents)
        return self.thinkBehavior(vision, availableMoves)

    # Greedy behavior thinking: purely react to vision-based information, moving toward the closest cell
    def thinkBehavior(self, vision, availableMoves) -> MoveType:
        # First priority: adjacent cell
        priorityMoves = [
            (MoveType.UP, vision[0][1]),  #  Top
            (MoveType.RIGHT, vision[1][2]),  #  Right
            (MoveType.DOWN, vision[2][1]),  # Bottom
            (MoveType.LEFT, vision[1][0]),  # Left
        ]

        for move, cell in priorityMoves:
            if move in availableMoves and cell == GridCellType.PARTIAL_EXPLORED.value:
                return move

        # Second priority: corner cell
        cornerMoves = [
            (MoveType.UP, MoveType.LEFT, vision[0][0]),  # Top-left corner
            (MoveType.UP, MoveType.RIGHT, vision[0][2]),  #  Top-right corner
            (MoveType.DOWN, MoveType.RIGHT, vision[2][2]),  #  Bottom-right corner
            (MoveType.DOWN, MoveType.LEFT, vision[2][0]),  # Bottom-left corner
        ]

        for moveOption1, moveOption2, cell in cornerMoves:
            if cell == GridCellType.PARTIAL_EXPLORED.value:
                if moveOption1 in availableMoves:
                    return moveOption1
                elif moveOption2 in availableMoves:
                    return moveOption2

        # No visible partially explored cell then random move
        return random.choice(list(availableMoves))
