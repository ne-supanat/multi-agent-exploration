from enum import Enum


class LayoutType(Enum):
    TEST = 0
    PLAIN = 1
    OBSTACLES = 2
    MAZE = 3
    DONUT_SHAPE = 4
    U_SHAPE = 5
    I_SHAPE = 6
    ROOM = 7
    HOUSE = 8
    CAVE = 9
    RL_PLAIN_SSM = -1
    RL_PLAIN_SM = -2
    RL_PLAIN = -3
    RL_OBSTACLES = -4
    RL_MAZE = -5
