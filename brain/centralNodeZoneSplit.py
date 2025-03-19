import math
from scipy.optimize import linear_sum_assignment
import numpy as np

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

        zones = []
        # Creating zone
        for i, agent in enumerate(self.agents):
            zone = []
            for rowIndex in range(zoneHeight):
                if (i * zoneHeight) + rowIndex >= shape[0]:
                    break
                for columnIndex in range(shape[1]):
                    zone.append((i * zoneHeight + rowIndex, columnIndex))

            zones.append(zone)

        # Aassigning zone to agent optimisation
        # Create distance matrix of each agent to centroid of each zone
        distanceMatrix = np.zeros((len(self.agents), len(zones)))

        for i, agent in enumerate(self.agents):
            for j, zone in enumerate(zones):
                # find approximate centroid of rectangle shape zone
                centerRow, centerColumn = (i * zoneHeight + 0.5 * zoneHeight), (
                    0.5 * shape[1]
                )

                # Manhattan distance
                distanceMatrix[i, j] = abs(centerRow - agent.row) + abs(
                    centerColumn - agent.column
                )

        # Find the closest zone for each agent
        # using assignment problem optimisation method
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html
        rowIndex, columnIndex = linear_sum_assignment(distanceMatrix)

        for i in rowIndex:
            agent = self.agents[i]
            self.agentTargetPool[agent.name] = zones[i]
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

    def recheckTargetQueues(self, agent):
        for agent in self.agents:
            for pos in self.agentsTargetQueue[agent.name]:
                if self.sharedMemory.map[pos[0], pos[1]] in [
                    GridCellType.WALL.value,
                    GridCellType.EXPLORED.value,
                ]:
                    self.agentsTargetQueue[agent.name].remove(pos)
