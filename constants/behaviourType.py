from enum import Enum


class BehaviourType(Enum):
    # Independent behaviour
    WANDERING = 1.1
    GREEDY = 1.2
    REINFORCEMENT = 1.3
    # Distributed behaviour
    FRONTIER = 2.1
    GREEDY_FRONTIER = 2.2
    # Centralised behaviour
    FRONTIER_CENTRAL_FIFO = 3.1
    FRONTIER_CENTRAL_GREEDY = 3.2
