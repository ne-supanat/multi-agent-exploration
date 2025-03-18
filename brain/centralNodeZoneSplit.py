import math

from brain.centralNode import CentralNode
from sharedMemory import SharedMemory

from constants.gridCellType import GridCellType


from dijkstraMap import dijkstraMap, dijkstraSearch


class CentralNodeZoneSplit(CentralNode):
    def __init__(self, agents, sharedMemory):
        super().__init__(agents, sharedMemory)

        self.agentTargetPool = {}

        for agent in agents:
            self.agentsTargetQueue[agent.name] = []
            self.agentTargetPool[agent.name] = []

        self.planAll()

    # Central greedy planing: assign frontier to closest agent
    def planAll(self):
        shape = self.sharedMemory.map.shape

        zoneHeight = math.ceil(shape[0] / len(self.agents))

        for i, agent in enumerate(self.agents):
            for rowIndex in range(zoneHeight):
                if (i * zoneHeight) + rowIndex >= shape[0]:
                    break
                for columnIndex in range(shape[1]):
                    self.agentTargetPool[agent.name].append(
                        (i * zoneHeight + rowIndex, columnIndex)
                    )

        for agent in self.agents:
            self.planOne(agent)

    # Planing a sequence of target for one agent
    def planOne(self, agent):
        self.findClosestFrontier(agent)

    def findClosestFrontier(self, agent):
        if len(self.agentTargetPool[agent.name]) > 0:
            distanceMap = dijkstraMap(self.sharedMemory.map, agent.getPosition())
            closestCell = dijkstraSearch(distanceMap, self.agentTargetPool[agent.name])

            if closestCell:
                self.agentsTargetQueue[agent.name].append(closestCell)
                self.agentTargetPool[agent.name].remove(closestCell)

    def recheckTargetQueues(self, vision, agent):
        for agent in self.agents:
            for pos in self.agentsTargetQueue[agent.name]:
                if self.sharedMemory.map[pos[0], pos[1]] in [
                    GridCellType.WALL.value,
                    GridCellType.EXPLORED.value,
                ]:
                    self.agentsTargetQueue[agent.name].remove(pos)
