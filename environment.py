import tkinter as tk
import numpy as np
import matplotlib as mpl

from constants.layoutType import LayoutType
from constants.gridCellType import GridCellType
from imageToArray import imageToArray


# Modification of university of nottingham COMP4105 24-25 module's material
class Environment:
    def __init__(
        self,
        layoutType: LayoutType = None,
        colormap: str = "YlOrBr",
        heatmapValueMax: int = 5,
    ):
        self.cellSize = 10  # Pixels per grid cell
        self.gridSize = (0, 0)
        self.gridMap = np.full((0, 0), GridCellType.UNEXPLORED.value, dtype=int)
        self.gridMapCurrent = np.full((0, 0), GridCellType.UNEXPLORED.value, dtype=int)
        self.layoutType = layoutType

        # Heatmap visualisation parameter
        self.colormap = colormap
        self.heatmapValueMax = heatmapValueMax  # maximun value in heatmap
        self.heatMapCurrent = np.zeros((0, 0), dtype=int)

        if layoutType != None:
            self.setupLayout(layoutType)

    def reset(self):
        self.setupLayout(self.layoutType)

    def setupLayout(self, layoutType) -> np.ndarray:
        layout = None
        if layoutType == LayoutType.TEST:
            layout = self.setupLayoutTest()
        elif layoutType == LayoutType.PLAIN:
            layout = self.setupLayoutPlain()
        elif layoutType == LayoutType.OBSTACLES:
            layout = self.setupLayoutObstacles()
        elif layoutType == LayoutType.MAZE:
            layout = self.setupLayoutMaze()
        elif layoutType == LayoutType.U_SHAPE:
            layout = self.setupLayoutUShape()
        elif layoutType == LayoutType.I_SHAPE:
            layout = self.setupLayoutIShape()
        elif layoutType == LayoutType.O_SHAPE:
            layout = self.setupLayoutOShape()
        elif layoutType == LayoutType.ROOM:
            layout = self.setupLayoutRoom()
        elif layoutType == LayoutType.HOUSE:
            layout = self.setupLayoutHouse()
        elif layoutType == LayoutType.CAVE:
            layout = self.setupLayoutCave()
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
        self.gridMapCurrent = self.gridMap.copy()
        self.heatMapCurrent = np.zeros(self.gridSize, dtype=int)
        return layout

    def setupLayoutTest(self):

        # self.gridSize = (8, 8)  # row, column
        # self.gridMap = np.full(self.gridSize, GridCellType.UNEXPLORED.value, dtype=int)

        # self.gridMap[1, 1] = GridCellType.WALL.value
        # self.gridMap[1, 6] = GridCellType.WALL.value
        # self.gridMap[6, 1] = GridCellType.WALL.value
        # self.gridMap[6, 6] = GridCellType.WALL.value

        self.gridSize = (15, 15)  # row, column
        self.gridMap = np.full(self.gridSize, GridCellType.UNEXPLORED.value, dtype=int)

        self.gridMap[0:14, 0:13] = GridCellType.WALL.value
        self.gridMap[0:13, 0:14] = GridCellType.WALL.value

        # self.gridMap[1, 1] = GridCellType.WALL.value
        # self.gridMap[1, 3] = GridCellType.WALL.value
        # self.gridMap[3, 1] = GridCellType.WALL.value
        # self.gridMap[3, 3] = GridCellType.WALL.value

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

    def setupLayoutIShape(self):
        self.gridSize = (30, 25)  # row, column
        self.gridMap = imageToArray("cw/images/exp_i.png", 30, 25)

    def setupLayoutOShape(self):
        self.gridSize = (25, 25)  # row, column
        self.gridMap = imageToArray("cw/images/exp_donut.png", 25, 25)

    def setupLayoutRoom(self):
        self.gridSize = (25, 25)  # row, column
        self.gridMap = imageToArray("cw/images/exp_room.png", 25, 25)

    def setupLayoutHouse(self):
        self.gridSize = (50, 50)  # row, column
        self.gridMap = imageToArray("cw/images/exp_house.png", 50, 50)

    def setupLayoutCave(self):
        self.gridSize = (50, 50)  # row, column
        self.gridMap = imageToArray("cw/images/exp_cave.png", 50, 50)

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

    def drawGridVisualBase(self, canvas: tk.Canvas):
        # """Draw the grid and agents in Tkinter Canvas."""
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

        self.gridMapCurrent = self.gridMap.copy()

    def updateGridVisual(self, canvas: tk.Canvas):
        # """Draw the grid and agents in Tkinter Canvas."""
        # canvas.delete("grid")

        row, column = self.gridMap.shape

        for r in range(row):
            for c in range(column):
                if GridCellType.getColor(self.gridMap[r, c]) != GridCellType.getColor(
                    self.gridMapCurrent[r, c]
                ):
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

        self.gridMapCurrent = self.gridMap.copy()

    def drawGridHeatmapInfo(self, canvas: tk.Canvas):
        row, column = self.gridMap.shape
        visualGridWidth = column * self.cellSize
        visualGridHeight = row * self.cellSize

        heatmapValueMax = self.heatmapValueMax
        colormap = mpl.colormaps[self.colormap].resampled(heatmapValueMax)

        # Create heatmap description
        # format:
        # ===========
        # Visited heatmap
        # 0 colormap[0]...colormap[5] 5
        # ===========

        canvas.create_text(
            visualGridWidth + 10,
            visualGridHeight + 15,
            anchor="w",
            text=f"Visited heatmap",
        )

        canvas.create_text(
            visualGridWidth + 10,
            visualGridHeight + 30,
            anchor="w",
            text=f"0",
        )

        for value in range(heatmapValueMax):
            x1, y1 = value * self.cellSize, 0
            x2, y2 = x1 + self.cellSize, y1 + self.cellSize

            color = colormap(value)
            colorCode = self.getColorCode(color)

            canvas.create_rectangle(
                visualGridWidth + 25 + x1,
                visualGridHeight + y1 + 25,
                visualGridWidth + 25 + x2,
                visualGridHeight + y2 + 25,
                fill=colorCode,
            )

        canvas.create_text(
            visualGridWidth + 25 + (heatmapValueMax * self.cellSize) + 10,
            visualGridHeight + 30,
            anchor="w",
            text=f"{heatmapValueMax}",
        )

    def drawGridHeatmapBase(self, canvas: tk.Canvas):
        # """Draw the grid and agents in Tkinter Canvas."""
        canvas.delete("gridHeatmap")

        row, column = self.gridMap.shape
        visualGridWidth = column * self.cellSize

        heatmapValueMax = self.heatmapValueMax
        colormap = mpl.colormaps[self.colormap].resampled(heatmapValueMax)

        for r in range(row):
            for c in range(column):
                x1, y1 = c * self.cellSize, r * self.cellSize
                x2, y2 = x1 + self.cellSize, y1 + self.cellSize

                value = self.heatMapCurrent[r, c]

                # NOTE: type of value affect returned color
                # int: 0, 1, 2, ..., valueCap
                # float: 0.0, 0.1, 0.2 , ..., 1.0
                color = colormap(value if value < heatmapValueMax else heatmapValueMax)
                colorCode = self.getColorCode(color)

                canvas.create_rectangle(
                    visualGridWidth + x1,
                    y1,
                    visualGridWidth + x2,
                    y2,
                    fill=colorCode,
                    # outline="white",
                    tags="grid",
                )
                canvas.tag_lower("gridHeatmap")

    def updateGridHeatmap(self, canvas: tk.Canvas, heatmap):
        # """Draw the grid and agents in Tkinter Canvas."""
        row, column = self.gridMap.shape
        visualGridWidth = column * self.cellSize

        heatmapValueMax = self.heatmapValueMax
        colormap = mpl.colormaps[self.colormap].resampled(heatmapValueMax)

        for r in range(row):
            for c in range(column):
                value = heatmap[r, c]

                # NOTE: type of value affect returned color
                # int: 0, 1, 2, ..., valueCap
                # float: 0.0, 0.1, 0.2 , ..., 1.0
                if (
                    heatmap[r, c] != self.heatMapCurrent[r, c]
                    and heatmap[r, c] <= heatmapValueMax
                ):
                    color = colormap(
                        value if value < heatmapValueMax else heatmapValueMax
                    )
                    colorCode = self.getColorCode(color)

                    x1, y1 = c * self.cellSize, r * self.cellSize
                    x2, y2 = x1 + self.cellSize, y1 + self.cellSize

                    canvas.create_rectangle(
                        visualGridWidth + x1,
                        y1,
                        visualGridWidth + x2,
                        y2,
                        fill=colorCode,
                        # outline="white",
                        tags="grid",
                    )

        self.heatMapCurrent = heatmap.copy()

    def getColorCode(self, rgba):
        # Create color code
        r, g, b = int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255)
        return f"#{r:02x}{g:02x}{b:02x}"

    def getMapSize(self):
        row, column = self.gridMap.shape
        return (row * self.cellSize, column * self.cellSize)

    def totalCellOpen(self):
        return self.gridMap.size - np.count_nonzero(
            self.gridMap == GridCellType.WALL.value
        )

    def totalCellExplored(self):
        return np.count_nonzero(self.gridMap == GridCellType.EXPLORED.value)

    def currentCoverage(self):
        openCell = self.totalCellOpen()
        exploredCell = self.totalCellExplored()

        exploredRatio = exploredCell / openCell
        return exploredRatio * 100

    def isFullyExplored(self):
        return np.all(
            np.isin(
                self.gridMap, [GridCellType.WALL.value, GridCellType.EXPLORED.value]
            )
        )
