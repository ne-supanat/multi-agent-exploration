import random
import numpy as np

from constants.gridCellType import GridCellType
from constants.behaviourType import BehaviourType
from constants.moveType import MoveType


class Brain:

    def __init__(self, agent, behaviour: BehaviourType):
        self.agent = agent
        # self.path = aStarSearch(self.map)
        # print(self.path)
        self.behaviour = behaviour

    # Decide what should be the next move
    def thinkAndAct(self, vision, agents) -> MoveType:
        availableMoves = self.checkAvailableMoves(vision, agents)

        if self.behaviour == BehaviourType.WANDERING:
            return self.thinkWandering(availableMoves)
        else:
            return MoveType.STAY

    def checkAvailableMoves(self, vision, agents: list) -> MoveType:
        # All move type are available at first step
        availableMoves = set(MoveType)

        # Prevent hit wall and other agents
        # by filter move in that direction out if there are walls or agents
        availableMoves = self.checkWalls(availableMoves, vision)
        availableMoves = self.checkAgents(availableMoves, agents)

        return availableMoves

    def checkWalls(self, availableMoves: set[MoveType], vision) -> set[MoveType]:
        if vision[0][1] == GridCellType.WALL.value:  # check top postition
            availableMoves.discard(MoveType.UP)
        if vision[2][1] == GridCellType.WALL.value:  # check bottom postition
            availableMoves.discard(MoveType.DOWN)
        if vision[1][0] == GridCellType.WALL.value:  # check left postition
            availableMoves.discard(MoveType.LEFT)
        if vision[1][2] == GridCellType.WALL.value:  # check right postition
            availableMoves.discard(MoveType.RIGHT)

        return availableMoves

    def checkAgents(self, availableMoves: set[MoveType], agents: list) -> set[MoveType]:
        for agent in agents:
            if agent.name == self.agent:
                continue

            if agent.x == self.agent.x:
                if agent.y == self.agent.y - 1:
                    availableMoves.discard(MoveType.UP)  # check top postition
                elif agent.y == self.agent.y + 1:
                    availableMoves.discard(MoveType.DOWN)  # check bottom postition
            elif agent.y == self.agent.y:
                if agent.x == self.agent.x + 1:
                    availableMoves.discard(MoveType.RIGHT)  # check right postition
                elif agent.x == self.agent.x - 1:
                    availableMoves.discard(MoveType.LEFT)  # check left postition

        return availableMoves

    # Wandering behavior thinking: randomly move
    def thinkWandering(self, availableMoves) -> MoveType:
        return random.choice(list(availableMoves))


class Agent:

    def __init__(self, name, cellSize, behaviourType: BehaviourType):
        self.name = name
        self.x = 1
        self.y = 1
        self.cellSize = cellSize
        self.vision = np.zeros((3, 3))  # simulate limited vision only 1 cell around
        self.map = np.zeros((15, 15))
        self.brain = Brain(self, behaviourType)

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
