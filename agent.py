import random
import numpy as np

from constants.gridCellType import GridCellType


class Agent:

    def __init__(self, namep, cellSize):
        self.name = namep
        self.x = 1
        self.y = 1
        self.cellSize = cellSize
        self.map = np.zeros((3, 3))

    # draws the agent at its current position
    def draw(self, canvas):
        radius = self.cellSize / 2
        centerX = (self.x * self.cellSize) + radius
        centerY = (self.y * self.cellSize) + radius
        canvas.create_oval(
            centerX - radius,
            centerY - radius,
            centerX + radius,
            centerY + radius,
            fill="blue",
            outline="black",
            tags=self.name,
        )

    def setPosition(self, x, y):
        self.x = x
        self.y = y

    # What happen at each timestep
    def update(self, canvas, gridMap):
        for r in range(3):
            for c in range(3):
                self.map[r, c] = gridMap[self.y + r - 1, self.x + c - 1]

        self.move(canvas)

        return self.x, self.y

    # Handle movement
    def move(self, canvas):
        availableMovements = [self.stay]

        # TODO: not hit other agents
        if self.map[0][1] != GridCellType.WALL.value:
            availableMovements.append(self.moveUp)
        if self.map[2][1] != GridCellType.WALL.value:
            availableMovements.append(self.moveDown)
        if self.map[1][0] != GridCellType.WALL.value:
            availableMovements.append(self.moveLeft)
        if self.map[1][2] != GridCellType.WALL.value:
            availableMovements.append(self.moveRight)

        random.choice(availableMovements)()

        canvas.delete(self.name)
        self.draw(canvas)

    def stay(self):
        return

    def moveUp(self):
        self.y -= 1
        return

    def moveDown(self):
        self.y += 1
        return

    def moveRight(self):
        self.x += 1
        return

    def moveLeft(self):
        self.x -= 1
        return
