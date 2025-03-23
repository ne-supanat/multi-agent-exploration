from constants.moveType import MoveType

from sharedMemory import SharedMemory
from brain.brainFrontier import BrainFrontier
from constants.gridCellType import GridCellType


class BrainFrontierAssist(BrainFrontier):
    def __init__(self, agentp, layoutShape, sharedMemory: SharedMemory):
        BrainFrontier.__init__(self, agentp, layoutShape, sharedMemory)
        self.localFrontiers = []
        self.needHelpFrontierThreshold = 10
        self.needHelpDistance = 20
        self.needHelpMoveThreshold = 20
        self.onAssist = False
        self.moveCount = 0

    # Frontier Assit behavior thinking:
    # remember discovered frontier cells and call for help if needed
    def thinkBehavior(self, vision, agents: list) -> MoveType:
        # Reach target cell
        if self.agent.getPosition() == self.targetCell:
            self.sharedMemory.completeTask(self.agent.name)
            self.targetCell = None

            # Complete assist task
            if self.onAssist:
                self.onAssist = False

        if self.onAssist:
            # Check if close to caller
            # Distance to caller (Manhattan distance)
            targetCaller = None
            for caller in self.sharedMemory.helpBoard:
                if self.sharedMemory.helpBoard[caller] == self.agent.name:
                    targetCaller = caller

            distanceToCaller = float("inf")
            for agent in agents:
                if agent.name == targetCaller:
                    distanceToCaller = abs(self.agent.row - agent.row) + abs(
                        self.agent.column - agent.column
                    )

            if distanceToCaller < self.needHelpDistance * 0.75:
                self.sharedMemory.completeTask(self.agent.name)
                self.targetCell = None
                self.onAssist = False

                for caller in self.sharedMemory.helpBoard:
                    if self.sharedMemory.helpBoard[caller] == self.agent.name:
                        self.sharedMemory.helpBoard.pop(caller)
                        break

        # Remove current position from frontier list
        if self.agent.getPosition() in self.sharedMemory.frontiers:
            self.sharedMemory.removeFrontier(self.agent.getPosition())

        for visionRow in range(vision.shape[0]):
            for visionColumn in range(vision.shape[1]):
                targetRow = self.agent.row + visionRow - 1
                targetColumn = self.agent.column + visionColumn - 1

                # Add new fronteir
                self.updateFrontier(
                    targetRow, targetColumn, vision[visionRow][visionColumn]
                )

                if (targetRow, targetColumn) not in self.localFrontiers:
                    self.localFrontiers.append((targetRow, targetColumn))

        # Remove explored area from local memory
        for frontier in self.localFrontiers:
            if (
                self.sharedMemory.map[frontier[0], frontier[1]]
                != GridCellType.PARTIAL_EXPLORED.value
            ):
                self.localFrontiers.remove(frontier)

        if not len(self.localFrontiers):
            self.sharedMemory.readyForHelp.append(self.agent.name)
        elif self.agent.name in self.sharedMemory.readyForHelp:
            self.sharedMemory.readyForHelp.remove(self.agent.name)

        if self.agent.name in list(self.sharedMemory.helpBoard.values()):
            self.onAssist = True

        # Call for help if needed
        # Check if already call for help
        if self.agent.name not in self.sharedMemory.helpBoard:
            # Can call for help every 20 moves
            # (reduce number of call for help: reduce computation)
            if (
                len(self.localFrontiers) > self.needHelpFrontierThreshold
                and self.moveCount > self.needHelpMoveThreshold
            ):
                self.moveCount = 0

                distances = []

                # Check if stay too far from other agents
                for agent in self.sharedMemory.readyForHelp:
                    # not self or on other agent's assistant
                    if agent.name == self.agent.name:
                        continue

                    # Manhattan distance
                    distance = abs(self.agent.row - agent.row) + abs(
                        self.agent.column - agent.column
                    )

                    distances.append((agent.name, distance))

                distances.sort(key=lambda x: x[1])

                if distances:
                    minDistance = distances[0][1]

                    if minDistance > self.needHelpDistance:
                        self.sharedMemory.helpBoard[self.agent.name] = distances[0][0]
                        self.sharedMemory.signUpOnTask(
                            distances[0][0], self.agent.getPosition()
                        )
            else:
                self.moveCount += 1

        bestMove = self.findBestMove()

        return bestMove

        # ======

    def findBestMove(self):
        # Recall & check self target cell with blackboard
        if self.agent.name in self.sharedMemory.blackboard:
            self.targetCell = self.sharedMemory.blackboard[self.agent.name]

        # Handle case target cell already got explored by other agent
        # send event similar to completed by itself
        # ** except on assist task **
        if not self.onAssist and (
            self.targetCell
            and (
                self.localMap[self.targetCell[0], self.targetCell[1]]
                == GridCellType.EXPLORED.value
            )
        ):
            self.sendCompleteTask()

        # Find new target cell
        # if currently not have one
        if self.targetCell == None:
            self.findNewTargetCell()

        bestMove = self.decideMove()

        return bestMove
