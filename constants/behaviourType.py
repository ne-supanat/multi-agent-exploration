from enum import Enum


class BehaviourType(Enum):
    WANDERING = 1
    GREEDY = 2
    FRONTIER = 3
    FRONTIER_CENTRAL_FIFO = 4
    REINFORCEMENT = 5
    GREEDY_FRONTIER = 6
