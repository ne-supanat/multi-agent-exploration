from enum import Enum


class LayoutType(Enum):
    TEST = 0
    PLAIN = 1
    OBSTACLES = 2
    MAZE = 3
    DONUT_SHAPE = 4
    U_SHAPE = 5
    ROOM = 6
    RL_PLAIN_SSM = -1
    RL_PLAIN_SM = -2
    RL_PLAIN = -3
    RL_OBSTACLES = -4
    RL_MAZE = -5
