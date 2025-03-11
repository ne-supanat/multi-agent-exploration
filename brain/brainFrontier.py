import numpy as np
import random

from constants.moveType import MoveType
from constants.gridCellType import GridCellType

from brain.brain import Brain
from centralMemory import CentralMap

from aStar import aStarSearch


# TODO: reassign job if candidate more suitable (no other task left)
class BrainFrontier(Brain):
    def __init__(self, agentp, centralMap: CentralMap = None):
        self.agent = agentp
        self.localRow = agentp.row
        self.localColumn = agentp.column
        self.localMap = centralMap if not centralMap is None else agentp.vision.copy()
        self.targetCell = None
        self.queue = []
        self.stuck = 0

    # Decide what should be the next move
    def thinkAndAct(self, vision, agents: list) -> MoveType:
        self.updateLocalMapSize(vision)
        self.gainInfoFromVision(vision)
        availableMoves = self.checkAvailableMoves(vision, agents)

        # print(self.localMap.map)
        if self.agent.name in self.localMap.blackboard:
            self.targetCell = self.localMap.blackboard[self.agent.name]

        # Find new target cell
        # if agent on target cell position or
        # target cell already got explored (not in fronteir anymore)
        if (
            (self.localRow, self.localColumn) == self.targetCell
            or (not self.targetCell in self.localMap.frontiers)
            or self.targetCell == None
        ):
            self.targetCell = None
            self.findNewTargetCell()

        # if stuck for too long (3 turns) give up on task
        if self.targetCell and self.stuck > 2:
            self.stuck = 0
            self.localMap.giveUpOnTask(self.targetCell)
            return MoveType.STAY

        # Planing path for new target or stuck try find new path
        if not self.queue or self.stuck > 0:
            self.planNewPath()

        if self.queue:
            # Move following sequence in queue if possible
            if self.queue[0] in availableMoves:
                bestMove = self.queue.pop(0)
            else:
                # If not movable then update stuck count
                self.stuck += 1
                bestMove = MoveType.STAY
        else:
            bestMove = MoveType.STAY

        self.updateLocalPostion(bestMove)

        # Remove current position from frontier list
        if (self.localRow, self.localColumn) in self.localMap.frontiers:
            self.localMap.removeFrontier((self.localRow, self.localColumn))

        return bestMove

    def updateLocalPostion(self, moveType: MoveType):
        if moveType == MoveType.UP:
            self.localRow -= 1
        elif moveType == MoveType.DOWN:
            self.localRow += 1
        elif moveType == MoveType.LEFT:
            self.localColumn -= 1
        elif moveType == MoveType.RIGHT:
            self.localColumn += 1

    # Update shape of local map
    def updateLocalMapSize(self, vision):
        visionRows, visionColumns = vision.shape[0], vision.shape[1]
        visionHalfRows = int(visionRows // 2)
        visionHalfColumns = int(visionColumns // 2)

        # Add new column(s)
        # Vision reach outside of known map (Left)
        if self.localColumn - visionHalfColumns < 0:
            self.localMap.addColumnLeft(visionHalfColumns)
            self.localColumn += 1  # compensate column postion due to new added column
            self.localMap.frontiers = [
                (frontier[0] + visionHalfColumns, frontier[1])
                for frontier in self.localMap.frontiers
            ]
        # vision reach outside of known map (Right)
        if self.localColumn + visionHalfColumns >= self.localMap.map.shape[1]:
            self.localMap.addColumnRight(visionHalfColumns)

        # Add new row(s)
        # vision reach outside of known map (Above)
        if self.localRow - visionHalfRows < 0:
            self.localMap.addRowAbove(visionHalfRows)
            self.localRow += 1  # compensate row postion due to new added row
            self.localMap.frontiers = [
                (frontier[0], frontier[1] + visionHalfRows)
                for frontier in self.localMap.frontiers
            ]

        # vision reach outside of known map (Below)
        if self.localRow + visionHalfRows >= self.localMap.map.shape[0]:
            self.localMap.addRowBelow(visionHalfRows)

    def gainInfoFromVision(self, vision):
        # Update local map with value from vision
        visionRows, visionColumns = vision.shape

        for visionRow in range(visionRows):
            for visionColumn in range(visionColumns):
                targetRow = self.localRow + visionRow - int(visionRows // 2)
                targetColumn = self.localColumn + visionColumn - int(visionColumns // 2)

                self.updateLocalMapValue(
                    targetRow, targetColumn, vision[visionRow][visionColumn]
                )

                # Add new fronteir
                self.updateFronteir(
                    targetRow, targetColumn, vision[visionRow][visionColumn]
                )

    def updateLocalMapValue(self, row, column, value):
        self.localMap.updateValueAt(row, column, value)

    def updateFronteir(self, row, column, value):
        if value == GridCellType.PARTIAL_EXPLORED.value and (
            not (row, column) in self.localMap.frontiers
        ):
            self.localMap.addFrontier((row, column))

    def findNewTargetCell(self):
        # Find the closest cell from frontier list
        if len(self.localMap.frontiers) > 0:
            closestFrontier = None
            closestDistance = float("inf")

            for frontier in self.localMap.frontiers:
                fronteirRow, fronteirColumn = frontier

                distance = abs(fronteirRow - self.localRow) + abs(
                    fronteirColumn - self.localColumn
                )

                if distance < closestDistance:
                    closestDistance = distance
                    closestFrontier = frontier

            self.targetCell = closestFrontier
            self.planNewPath()

            # Unassign from other agent
            for agent in self.localMap.blackboard:
                if self.targetCell == self.localMap.blackboard[agent]:
                    self.localMap.blackboard[agent] = None

            # Update assigned fronteir on shared blackboard
            self.localMap.blackboard[self.agent.name] = self.targetCell

    def planNewPath(self):
        self.queue.clear()

        # If no place assigned then stay
        if self.targetCell is None:
            self.queue.append(MoveType.STAY)
            return

        # Search best path using A* algorithm
        # path is in format of [(row, column), ...]
        path = aStarSearch(
            self.localMap.map, (self.localRow, self.localColumn), self.targetCell
        )

        # Finding path fail then wait
        if path is None:
            self.queue.append(MoveType.STAY)
            return

        # Create sequence of movement following path from A*
        for i in range(len(path) - 1):
            pCurrent = path[i]
            pNext = path[i + 1]

            pCurrentRow, pCurrentColumn = pCurrent
            pNextRow, pNextColumn = pNext

            if pCurrentRow > pNextRow:
                self.queue.append(MoveType.UP)
            if pCurrentRow < pNextRow:
                self.queue.append(MoveType.DOWN)
            if pCurrentColumn > pNextColumn:
                self.queue.append(MoveType.LEFT)
            if pCurrentColumn < pNextColumn:
                self.queue.append(MoveType.RIGHT)
