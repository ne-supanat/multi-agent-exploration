import tkinter as tk
import numpy as np

from constants.layoutType import LayoutType
from constants.gridCellType import GridCellType

# Modification of university of nottingham COMP4105 24-25 module's material


class Environment:
    # TODO: agents starting points
    def __init__(self, layoutType: LayoutType):
        self.cellSize = 20  # Pixels per grid cell
        self.gridSize = (0, 0)
        self.gridMap = np.full((0, 0), GridCellType.UNEXPLORED.value, dtype=int)

        self.setupLayout(layoutType)

    def setupLayout(self, layoutType) -> np.ndarray:
        layout = None
        if layoutType == LayoutType.TEST:
            layout = self.setupLayoutTest()
        if layoutType == LayoutType.PLAIN:
            layout = self.setupLayoutPlain()
        elif layoutType == LayoutType.OBSTACLES:
            layout = self.setupLayoutObstacles()
        # TODO:
        # elif layoutType == LayoutType.MAZE:
        #     layout = self.setupLayoutPlain()
        # elif layoutType == LayoutType.DONUT_SHAPE:
        #     layout = self.setupLayoutPlain()
        # elif layoutType == LayoutType.U_SHAPE:
        #     layout = self.setupLayoutPlain()

        self.createBoundary()
        return layout

    def setupLayoutTest(self):
        self.gridSize = (5, 10)  # row, column
        self.gridMap = np.full(self.gridSize, GridCellType.UNEXPLORED.value, dtype=int)

        # self.gridMap[1, 1:8] = GridCellType.EXPLORED.value
        # self.gridMap[2, 1:9] = GridCellType.PARTIAL_EXPLORED.value

    def setupLayoutPlain(self):
        self.gridSize = (30, 30)  # row, column
        self.gridMap = np.full(self.gridSize, GridCellType.UNEXPLORED.value, dtype=int)

    def setupLayoutObstacles(self):
        self.gridSize = (30, 30)  # row, column
        self.gridMap = np.full(self.gridSize, GridCellType.UNEXPLORED.value, dtype=int)

        self.gridMap[0:10, 10] = GridCellType.WALL.value
        self.gridMap[16, 5:16] = GridCellType.WALL.value
        self.gridMap[15:29, 20] = GridCellType.WALL.value

    def createBoundary(self):
        self.gridMap[0 : self.gridSize[0], 0] = GridCellType.WALL.value
        self.gridMap[0 : self.gridSize[0], self.gridSize[1] - 1] = (
            GridCellType.WALL.value
        )
        self.gridMap[0, 0 : self.gridSize[1]] = GridCellType.WALL.value
        self.gridMap[self.gridSize[0] - 1, 0 : self.gridSize[1]] = (
            GridCellType.WALL.value
        )

    def createCanvas(self, window: tk.Canvas):
        canvas = tk.Canvas(
            window,
            width=self.gridSize[1] * self.cellSize,
            height=self.gridSize[0] * self.cellSize + 40,
        )
        return canvas

    def drawGrid(self, canvas: tk.Canvas):
        """Draw the grid and agents in Tkinter Canvas."""
        canvas.delete("grid")

        row, column = self.gridMap.shape

        for r in range(row):
            for c in range(column):
                x1, y1 = c * self.cellSize, r * self.cellSize
                x2, y2 = x1 + self.cellSize, y1 + self.cellSize
                canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=GridCellType.getColor(self.gridMap[r, c]),
                    outline="white",
                    tags="grid",
                )
                canvas.tag_lower("grid")

    def getMapSize(self):
        row, column = self.gridMap.shape
        return (row * self.cellSize, column * self.cellSize)

    def isFullyExplored(self):
        return np.all(np.isin(self.gridMap, [-1, 2]))
