import numpy as np
from constants.gridCellType import GridCellType


class CentralMap:
    def __init__(self, sizeRow, sizeColumn):
        self.map = np.full(
            (sizeRow, sizeColumn), GridCellType.UNEXPLORED.value, dtype=int
        )
        self.frontiers = []
        self.blackboard = {}  # in format of (cell_row, cell_column): agent_name

    def addRowAbove(self, noOfRows):
        self.map = np.vstack(
            (
                np.full(
                    (noOfRows, self.map.shape[1]),
                    GridCellType.UNEXPLORED.value,
                    dtype=int,
                ),
                self.map,
            )
        )

    def addRowBelow(self, noOfRows):
        self.map = np.vstack(
            (
                self.map,
                np.full(
                    (noOfRows, self.map.shape[1]),
                    GridCellType.UNEXPLORED.value,
                    dtype=int,
                ),
            )
        )

    def addColumnLeft(self, noOfColumns):
        self.map = np.hstack(
            (
                np.full(
                    (self.map.shape[0], noOfColumns),
                    GridCellType.UNEXPLORED.value,
                    dtype=int,
                ),
                self.map,
            )
        )

    def addColumnRight(self, noOfColumns):
        self.map = np.hstack(
            (
                self.map,
                np.full(
                    (self.map.shape[0], noOfColumns),
                    GridCellType.UNEXPLORED.value,
                    dtype=int,
                ),
            )
        )

    def updateValueAt(self, row, column, value):
        self.map[row, column] = value

    def addFrontier(self, pos):
        self.frontiers.append(pos)

    def removeFrontier(self, pos):
        self.frontiers.remove(pos)

    def giveUpOnTask(self, targetCell):
        self.blackboard.pop(targetCell)
