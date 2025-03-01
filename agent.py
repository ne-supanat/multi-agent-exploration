import random
import numpy as np

from constants.moveType import MoveType
from brain.brain import Brain


class Agent:
    def __init__(self, name, cellSize):
        self.name = name
        self.x = 1
        self.y = 1
        self.cellSize = cellSize
        self.vision = np.zeros((3, 3))  # simulate limited vision only 1 cell around
        self.map = np.zeros((15, 15))

    def setBrain(self, brainp: Brain):
        self.brain = brainp

    def setPosition(self, x, y):
        self.x = x
        self.y = y

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

    # What happen at each timestep
    def update(self, canvas, gridMap, agents):
        for r in range(self.vision.shape[0]):
            for c in range(self.vision.shape[1]):
                self.vision[r, c] = gridMap[self.y + r - 1, self.x + c - 1]

        self.move(canvas, agents)

        return self.x, self.y

    # Handle movement
    def move(self, canvas, agents):
        moveType = self.brain.thinkAndAct(self.vision, agents)

        if moveType == MoveType.STAY:
            self.stay()
        elif moveType == MoveType.UP:
            self.moveUp()
        elif moveType == MoveType.DOWN:
            self.moveDown()
        elif moveType == MoveType.LEFT:
            self.moveLeft()
        elif moveType == MoveType.RIGHT:
            self.moveRight()

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
