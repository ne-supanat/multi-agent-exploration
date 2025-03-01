import random

from constants.moveType import MoveType

from brain.brain import Brain


class BrainWandering(Brain):
    # Wandering behavior thinking: randomly move
    def thinkBehavior(self, availableMoves) -> MoveType:
        return random.choice(list(availableMoves))
