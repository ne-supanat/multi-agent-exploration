import tkinter as tk
import numpy as np

from constants.layoutType import LayoutType
from constants.gridCellType import GridCellType
from imageToArray import imageToArray

# Modification of university of nottingham COMP4105 24-25 module's material

# TODO: generate randome map with connected open area?


class Environment:
    def __init__(self, layoutType: LayoutType = None):
        self.cellSize = 20  # Pixels per grid cell
        self.gridSize = (0, 0)
        self.gridMap = np.full((0, 0), GridCellType.UNEXPLORED.value, dtype=int)
        self.layoutType = layoutType

        if layoutType != None:
            self.setupLayout(layoutType)

    def reset(self):
        self.setupLayout(self.layoutType)

    def setupLayout(self, layoutType) -> np.ndarray:
        layout = None
        if layoutType == LayoutType.TEST:
            layout = self.setupLayoutTest()
        if layoutType == LayoutType.PLAIN:
            layout = self.setupLayoutPlain()
        elif layoutType == LayoutType.OBSTACLES:
            layout = self.setupLayoutObstacles()
        elif layoutType == LayoutType.MAZE:
            layout = self.setupLayoutMaze()
        elif layoutType == LayoutType.U_SHAPE:
            layout = self.setupLayoutUShape()
        elif layoutType == LayoutType.DONUT_SHAPE:
            layout = self.setupLayoutDonutShape()
        elif layoutType == LayoutType.ROOM:
            layout = self.setupLayoutRoom()
        elif layoutType == LayoutType.RL_PLAIN_SSM:
            layout = self.setupLayoutRLPlainSSM()
        elif layoutType == LayoutType.RL_PLAIN_SM:
            layout = self.setupLayoutRLPlainSM()
        elif layoutType == LayoutType.RL_PLAIN:
            layout = self.setupLayoutRLPlain()
        elif layoutType == LayoutType.RL_OBSTACLES:
            layout = self.setupLayoutRLObstacles()
        elif layoutType == LayoutType.RL_MAZE:
            layout = self.setupLayoutRLMaze()
        else:
            self.gridMap = np.full(
                self.gridSize, GridCellType.UNEXPLORED.value, dtype=int
            )

        self.createBoundary()
        return layout

    def setupLayoutTest(self):
        self.gridSize = (5, 5)  # row, column
        self.gridMap = np.full(self.gridSize, GridCellType.UNEXPLORED.value, dtype=int)

        # self.gridMap[1, 1:8] = GridCellType.EXPLORED.value
        # self.gridMap[2, 1:9] = GridCellType.PARTIAL_EXPLORED.value

    def setupLayoutPlain(self):
        self.gridSize = (25, 25)  # row, column
        self.gridMap = imageToArray("cw/images/exp_plain.png", 25, 25)

    def setupLayoutObstacles(self):
        self.gridSize = (25, 25)  # row, column
        self.gridMap = imageToArray("cw/images/exp_obs.png", 25, 25)

    def setupLayoutMaze(self):
        self.gridSize = (25, 25)  # row, column
        self.gridMap = imageToArray("cw/images/exp_maze.png", 25, 25)

    def setupLayoutUShape(self):
        self.gridSize = (25, 25)  # row, column
        self.gridMap = imageToArray("cw/images/exp_u.png", 25, 25)

    def setupLayoutDonutShape(self):
        self.gridSize = (25, 25)  # row, column
        self.gridMap = imageToArray("cw/images/exp_donut.png", 25, 25)

    def setupLayoutRoom(self):
        self.gridSize = (25, 25)  # row, column
        self.gridMap = imageToArray("cw/images/exp_room.png", 25, 25)

    def setupLayoutRLPlainSSM(self):
        self.gridSize = (5, 5)  # row, column
        self.gridMap = imageToArray("cw/images/rl_plain_ssm.png", 5, 5)

    def setupLayoutRLPlainSM(self):
        self.gridSize = (10, 10)  # row, column
        self.gridMap = imageToArray("cw/images/rl_plain_sm.png", 10, 10)

    def setupLayoutRLPlain(self):
        self.gridSize = (20, 20)  # row, column
        self.gridMap = imageToArray("cw/images/rl_plain.png", 20, 20)

    def setupLayoutRLObstacles(self):
        self.gridSize = (20, 20)  # row, column
        self.gridMap = imageToArray("cw/images/rl_obs.png", 20, 20)

    def setupLayoutRLMaze(self):
        self.gridSize = (20, 20)  # row, column
        self.gridMap = imageToArray("cw/images/rl_maze.png", 20, 20)

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
        return np.all(
            np.isin(
                self.gridMap, [GridCellType.WALL.value, GridCellType.EXPLORED.value]
            )
        )
