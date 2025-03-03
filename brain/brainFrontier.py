import numpy as np
import random

from constants.moveType import MoveType
from constants.gridCellType import GridCellType

from brain.brain import Brain
from centralMap import CentralMap

from aStar import a_star_search

# TODO: grid transpose?: prevent x,y row,column confusion
# TODO: select target cell algo: new type of brain?: (line 34:46)
# TODO: select target from farest cell instrad


# TODO: update frontier list from local map instead
class BrainFrontier(Brain):
    def __init__(self, agentp, centralMap: CentralMap = None):
        self.agent = agentp
        self.localX = agentp.x
        self.localY = agentp.y
        self.localMap = centralMap if not centralMap is None else agentp.vision.copy()
        self.targetCell = None
        self.queue = []

    # Decide what should be the next move
    def thinkAndAct(self, vision, agents: list) -> MoveType:
        self.updateLocalMapSize(vision)
        self.gainInfoFromVision(vision)
        availableMoves = self.checkAvailableMoves(vision, agents)

        # print(self.localMap.map)

        # TODO: add document comment
        if (self.localX, self.localY) == self.targetCell or (
            not self.targetCell in self.localMap.frontiers
        ):
            self.targetCell = None
            self.findNewTargetCell()

        # # Clear blackboard
        # self.localMap.blackboard = {
        #     k: v for k, v in self.localMap.blackboard.items() if v != self.agent.name
        # }
        # self.targetCell = None
        # self.findNewTargetCell()

        # plan path for new target or plan new path if cannot move toward that direction
        if not self.queue or (
            len(self.queue) > 0 and not self.queue[0] in availableMoves
        ):
            self.planPath()

        # If there is/are move(s) in queue do it first
        if len(self.queue) > 0:
            bestMove = self.queue.pop(0)
        else:
            bestMove = MoveType.STAY

        if bestMove in availableMoves:
            self.updateLocalPostion(bestMove)

            if (self.localX, self.localY) in self.localMap.frontiers:
                self.localMap.removeFrontierPos((self.localX, self.localY))

            return bestMove
        else:
            return MoveType.STAY

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
            self.localMap.addColumnLeft(horizontalRadius)
            self.localX += 1  # compensate x postion due to new added column
            self.localMap.frontiers = [
                (frontier[0] + 1, frontier[1]) for frontier in self.localMap.frontiers
            ]

            # print("add column left")
            # print(self.localMap.map)
        if self.localX + horizontalRadius >= self.localMap.map.shape[1]:
            self.localMap.addColumnRight(horizontalRadius)
            # print("add column right")
            # print(self.localMap.map)

        # Add new row(s)
        if self.localY - verticalRadius < 0:
            self.localMap.addRowAbove(verticalRadius)
            self.localY += 1  # compensate y postion due to new added row
            self.localMap.frontiers = [
                (frontier[0], frontier[1] + 1) for frontier in self.localMap.frontiers
            ]

            # print("add row above")
            # print(self.localMap.map)
        if self.localY + verticalRadius >= self.localMap.map.shape[0]:
            self.localMap.addRowBelow(verticalRadius)
            # print("add row below")
            # print(self.localMap.map)

    def gainInfoFromVision(self, vision):
        # Update local map with value from vision
        visionShapeRow, visionShapeColumn = vision.shape[0], vision.shape[1]
        for r in range(visionShapeRow):
            for c in range(visionShapeColumn):
                targetRow = self.localY + r - int(visionShapeRow // 2)
                targetColumn = self.localX + c - int(visionShapeColumn // 2)

                self.updateLocalMapValue(targetColumn, targetRow, vision[r][c])
                self.updateFronteir(targetColumn, targetRow, vision[r][c])

    def updateLocalMapValue(self, column, row, value):
        self.localMap.updateValueAt(column, row, value)

    def updateFronteir(self, column, row, value):
        if value == GridCellType.PARTIAL_EXPLORED.value and (
            not (column, row) in self.localMap.frontiers
        ):
            self.localMap.addFrontierPos((column, row))

    def findNewTargetCell(self):
        # Find the closest cell in frontiers
        if len(self.localMap.frontiers) > 0:
            closestFronteir = None
            closestDistance = float("inf")
            for fronteir in self.localMap.frontiers:
                if fronteir in self.localMap.blackboard:
                    continue

                distance = abs(fronteir[0] - self.localX) + abs(
                    fronteir[1] - self.localY
                )

                if distance < closestDistance:
                    closestDistance = distance
                    closestFronteir = fronteir

            self.targetCell = closestFronteir
            self.planPath()

            self.localMap.blackboard[self.targetCell] = self.agent.name

    def planPath(self):
        self.queue.clear()

        # If no place assigned then stay
        if self.targetCell is None:
            return MoveType.STAY

        path = a_star_search(
            self.localMap.map.transpose(), (self.localX, self.localY), self.targetCell
        )
        # print(path)

        if path is None:
            self.queue.append(MoveType.STAY)
            return

        for i in range(len(path) - 1):
            posCurrent = path[i]
            posNext = path[i + 1]

            if posNext[1] < posCurrent[1]:
                self.queue.append(MoveType.UP)
            if posNext[1] > posCurrent[1]:
                self.queue.append(MoveType.DOWN)
            if posNext[0] < posCurrent[0]:
                self.queue.append(MoveType.LEFT)
            if posNext[0] > posCurrent[0]:
                self.queue.append(MoveType.RIGHT)

        # print(self.queue)
