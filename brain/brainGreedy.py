import random

from constants.moveType import MoveType
from constants.gridCellType import GridCellType

from brain.brain import Brain


class BrainGreedy(Brain):
    # Decide what should be the next move
    def thinkAndAct(self, vision, agents: list) -> MoveType:
        availableMoves = self.checkAvailableMoves(vision, agents)
        return self.thinkBehavior(vision, availableMoves)

    # Wandering behavior thinking: randomly move
    def thinkBehavior(self, vision, availableMoves) -> MoveType:

        if vision[0][1] == GridCellType.PARTIAL_EXPLORED.value:
            return MoveType.UP
        if vision[1][0] == GridCellType.PARTIAL_EXPLORED.value:
            return MoveType.LEFT
        if vision[2][1] == GridCellType.PARTIAL_EXPLORED.value:
            return MoveType.DOWN
        if vision[1][2] == GridCellType.PARTIAL_EXPLORED.value:
            return MoveType.RIGHT

        return random.choice(list(availableMoves))
