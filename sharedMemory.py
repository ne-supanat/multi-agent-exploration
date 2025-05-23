import numpy as np
from constants.gridCellType import GridCellType


class SharedMemory:
    def __init__(self, shape):
        self.map = np.full(shape, GridCellType.UNEXPLORED.value, dtype=int)
        self.frontiers = []
        self.blackboard = {}  # in format of agent_name: (cell_row, cell_column)
        self.helpBoard = {}  # in format of caller_name: helper_name
        self.readyForHelp = []

    def addFrontier(self, pos):
        if not pos is None:
            self.frontiers.append(pos)

    def removeFrontier(self, pos):
        if pos in self.frontiers:
            self.frontiers.remove(pos)

    def signUpOnTask(self, agentName, targetCell):
        self.removeFrontier(targetCell)
        self.blackboard[agentName] = targetCell

    def completeTask(self, agentName):
        self.blackboard[agentName] = None

    def giveUpOnTask(self, agentName):
        self.addFrontier(self.blackboard[agentName])
        self.blackboard[agentName] = None
