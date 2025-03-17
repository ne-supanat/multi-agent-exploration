import random

from constants.moveType import MoveType

from brain.brain import Brain


class BrainWandering(Brain):
    # Wandering behavior thinking: randomly move
    def thinkBehavior(self, vision, agents) -> MoveType:
        return random.choice(list(self.availableMoves))
