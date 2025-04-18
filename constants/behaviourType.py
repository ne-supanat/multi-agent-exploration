from enum import Enum


class BehaviourType(Enum):
    # Independent behaviour
    WANDERING = 1.1
    GREEDY = 1.2
    # REINFORCEMENT = 1.3
    # Distributed behaviour
    FRONTIER = 2.1
    GREEDY_FRONTIER = 2.2
    FRONTIER_ASSIST = 2.3
    SCOUT = 2.4
    # Centralised behaviour
    FRONTIER_CENTRAL_FIFO = 3.1
    FRONTIER_CENTRAL_GREEDY = 3.2
    ZONE_SPLIT = 3.3
    ZONE_VORONOI = 3.4

    def getExperimentBehaviourType():
        return [
            type
            for type in BehaviourType
            if type
            not in [
                BehaviourType.FRONTIER_CENTRAL_FIFO,
            ]
        ]
