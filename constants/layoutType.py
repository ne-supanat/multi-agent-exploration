from enum import Enum


class LayoutType(Enum):
    TEST = 0
    PLAIN = 1
    OBSTACLES = 2
    MAZE = 3
    O_SHAPE = 4
    U_SHAPE = 5
    I_SHAPE = 6
    ROOM = 7
    HOUSE = 8
    CAVE = 9

    def getExperimentLayout():
        return [layout for layout in LayoutType if layout.value > 0]
