from enum import Enum


class GridCellType(Enum):
    WALL = -1
    UNEXPLORED = 0
    PARTIAL_EXPLORED = 1
    EXPLORED = 2

    # Return color base on cell type WALL (black), UNEXPLORED (gray), PARTIAL_EXPLORED (white), EXPLORED (blue)
    def getColor(type):
        return {
            -1: "black",
            0: "gray",
            1: "white smoke",
            2: "lightblue",
        }[type]


[]
