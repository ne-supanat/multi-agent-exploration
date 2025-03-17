import numpy as np
from constants.gridCellType import GridCellType


class SharedMemory:
    def __init__(self, sizeRow, sizeColumn):
        self.map = np.full(
            (sizeRow, sizeColumn), GridCellType.UNEXPLORED.value, dtype=int
        )
        self.frontiers = []
        self.blackboard = {}  # in format of (cell_row, cell_column): agent_name

    def updateValueAt(self, row, column, value):
        self.map[row, column] = value

    def addFrontier(self, pos):
        self.frontiers.insert(0, pos)

    def removeFrontier(self, pos):
        self.frontiers.remove(pos)

    def signUpOnTask(self, agentName, targetCell):
        self.removeFrontier(targetCell)
        self.blackboard[agentName] = targetCell

    def completeTask(self, agentName):
        self.blackboard[agentName] = None

    def giveUpOnTask(self, agentName):
        self.addFrontier(self.blackboard[agentName])
        self.blackboard[agentName] = None
