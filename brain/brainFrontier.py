import numpy as np
import random

from constants.moveType import MoveType
from constants.gridCellType import GridCellType

from brain.brain import Brain


class BrainFrontier(Brain):
    def __init__(self, agentp, centralMap=None):
        self.agent = agentp
        self.localMap = centralMap if centralMap != None else agentp.vision
        self.frontiers = []
        self.queue = []
        # self.path = aStarSearch(self.map)
        # print(self.path)

    # Decide what should be the next move
    def thinkAndAct(self, vision, agents: list) -> MoveType:
        self.updateLocalMapSize(vision)
        self.gainInfoFromVision(vision)
        availableMoves = self.checkAvailableMoves(vision, agents)

        print((self.agent.x, self.agent.y))

        if (self.agent.x, self.agent.y) in self.frontiers:
            self.frontiers.remove((self.agent.x, self.agent.y))

        # If there is/are move(s) in queue do it first
        if len(self.queue) > 0:
            return self.queue.pop(0)
        # If there is no move in queue
        # find the closest partially explored cell, add sequence of move toward it in queue
        elif len(self.queue) == 0:
            self.thinkBehavior(availableMoves)
            return self.queue.pop(0)
        # All cell should already be explored
        else:
            return MoveType.STAY

    # Update shape of local map
    def updateLocalMapSize(self, vision):
        visionShapeRow, visionShapeColumn = vision.shape[0], vision.shape[1]
        horizontalRadius = int(visionShapeRow // 2)
        verticalRadius = int(visionShapeColumn // 2)

        localMapShapeRow, localMapShapeColumn = (
            self.localMap.shape[0],
            self.localMap.shape[1],
        )

        # Add new column(s)
        if self.agent.x + horizontalRadius >= localMapShapeColumn:
            self.localMap = np.append(
                self.localMap,
                np.zeros((localMapShapeRow, 1)),
                axis=1,
            )

        # Add new row(s)
        if self.agent.y + verticalRadius >= localMapShapeRow:
            self.localMap = np.append(
                self.localMap,
                np.zeros((1, localMapShapeColumn)),
                axis=0,
            )

    def gainInfoFromVision(self, vision):
        # Update local map with value from vision
        visionShapeRow, visionShapeColumn = vision.shape[0], vision.shape[1]
        for r in range(visionShapeRow):
            for c in range(visionShapeColumn):
                targetY = self.agent.y + r - int(visionShapeRow // 2)
                targetX = self.agent.x + c - int(visionShapeColumn // 2)

                self.updateLocalMapValue(targetX, targetY, vision[r][c])
                self.updateFronteir(targetX, targetY, vision[r][c])

    def updateLocalMapValue(self, x, y, value):
        self.localMap[y, x] = value

    def updateFronteir(self, x, y, value):
        if value == GridCellType.PARTIAL_EXPLORED.value and (
            not (x, y) in self.frontiers
        ):
            self.frontiers.append((x, y))

    # Frontier behavior thinking: move to cloest partially explored cell
    def thinkBehavior(self, availableMoves) -> MoveType:
        # TODO: implement A* path
        # for cell in self.frontiers:
        #   astar to closest partially explored cell

        if len(self.frontiers) > 0:
            targetX, targetY = self.frontiers[0]

            if targetY < self.agent.y and MoveType.UP in availableMoves:
                self.queue.append(MoveType.UP)
            if targetY > self.agent.y and MoveType.DOWN in availableMoves:
                self.queue.append(MoveType.DOWN)
            if targetX < self.agent.x and MoveType.LEFT in availableMoves:
                self.queue.append(MoveType.LEFT)
            if targetX > self.agent.x and MoveType.RIGHT in availableMoves:
                self.queue.append(MoveType.RIGHT)
        else:
            self.queue.append(MoveType.STAY)
