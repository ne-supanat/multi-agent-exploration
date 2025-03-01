import numpy as np
import random

from constants.moveType import MoveType
from constants.gridCellType import GridCellType

from brain.brain import Brain


class BrainFrontier(Brain):
    def __init__(self, agentp, centralMap=None):
        self.agent = agentp
        self.localX = 1
        self.localY = 1
        self.localMap = centralMap if centralMap != None else agentp.vision.copy()
        self.frontiers = []
        self.queue = []
        # self.path = aStarSearch(self.map)
        # print(self.path)

    # Decide what should be the next move
    def thinkAndAct(self, vision, agents: list) -> MoveType:
        self.updateLocalMapSize(vision)
        self.gainInfoFromVision(vision)
        availableMoves = self.checkAvailableMoves(vision, agents)

        print(self.localMap)

        if (self.localX, self.localY) in self.frontiers:
            self.frontiers.remove((self.localX, self.localY))

        # If there is no move in queue
        # find the closest partially explored cell, add sequence of move toward it in queue
        if len(self.queue) == 0:
            self.thinkBehavior(availableMoves)

        # If there is/are move(s) in queue do it first
        if len(self.queue) > 0:
            bestMove = self.queue.pop(0)
        else:
            bestMove = MoveType.STAY

        self.updateLocalPostion(bestMove)
        return bestMove

    def updateLocalPostion(self, moveType: MoveType):
        if moveType == MoveType.UP:
            self.localY -= 1
        elif moveType == MoveType.DOWN:
            self.localY += 1
        elif moveType == MoveType.LEFT:
            self.localX -= 1
        elif moveType == MoveType.RIGHT:
            self.localX += 1

    # Update shape of local map
    def updateLocalMapSize(self, vision):
        visionShapeRow, visionShapeColumn = vision.shape[0], vision.shape[1]
        horizontalRadius = int(visionShapeRow // 2)
        verticalRadius = int(visionShapeColumn // 2)

        # Add new column(s)
        if self.localX - horizontalRadius < 0:
            self.localMap = np.hstack(
                (np.zeros((self.localMap.shape[0], horizontalRadius)), self.localMap)
            )
            self.localX += 1  # compensate x postion due to new added column
            self.frontiers = [
                (frontier[0] + 1, frontier[1]) for frontier in self.frontiers
            ]

            print("add column before")
            print(self.localMap)
        if self.localX + horizontalRadius >= self.localMap.shape[1]:
            self.localMap = np.hstack(
                (self.localMap, np.zeros((self.localMap.shape[0], horizontalRadius)))
            )

        # Add new row(s)
        if self.localY - verticalRadius < 0:
            self.localMap = np.vstack(
                (np.zeros((horizontalRadius, self.localMap.shape[1])), self.localMap)
            )
            self.localY += 1  # compensate y postion due to new added row
            self.frontiers = [
                (frontier[0], frontier[1] + 1) for frontier in self.frontiers
            ]

            print("add row before")
            print(self.localMap)
        if self.localY + verticalRadius >= self.localMap.shape[0]:
            self.localMap = np.vstack(
                (self.localMap, np.zeros((horizontalRadius, self.localMap.shape[1])))
            )

    def gainInfoFromVision(self, vision):
        # Update local map with value from vision
        visionShapeRow, visionShapeColumn = vision.shape[0], vision.shape[1]
        for r in range(visionShapeRow):
            for c in range(visionShapeColumn):
                targetY = self.localY + r - int(visionShapeRow // 2)
                targetX = self.localX + c - int(visionShapeColumn // 2)

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

            if targetY < self.localY and MoveType.UP in availableMoves:
                self.queue.append(MoveType.UP)
            if targetY > self.localY and MoveType.DOWN in availableMoves:
                self.queue.append(MoveType.DOWN)
            if targetX < self.localX and MoveType.LEFT in availableMoves:
                self.queue.append(MoveType.LEFT)
            if targetX > self.localX and MoveType.RIGHT in availableMoves:
                self.queue.append(MoveType.RIGHT)
        else:
            self.queue.append(MoveType.STAY)
