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
        self.blockedCells = set()

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
                centerRow, centerColumn = (j * zoneHeight + 0.5 * zoneHeight), (
                    0.5 * shape[1]
                )

                # Manhattan distance
                distanceMatrix[i, j] = abs(centerRow - agent.row) + abs(
                    centerColumn - agent.column
                )
        #            z1(10,20)  z2(30,20)
        # a0(35,35)  25,15: 40   5,15: 20
        # a1(10,35)   0,15: 15  20,15: 35

        # Find the closest zone for each agent
        # using assignment problem optimisation method
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html
        rowIndex, columnIndex = linear_sum_assignment(distanceMatrix)

        for i in rowIndex:
            agent = self.agents[i]
            self.agentTargetPool[agent.name] = zones[columnIndex[i]]
            self.planOne(agent)

    # Planing a sequence of target for one agent
    def planOne(self, agent):
        self.findClosestFrontier(agent)

    def findClosestFrontier(self, agent):
        if len(self.agentTargetPool[agent.name]) > 0:
            availablePool = [
                cell
                for cell in self.agentTargetPool[agent.name]
                if cell not in self.blockedCells
            ]
            distanceMap = dijkstraMap(
                self.sharedMemory.map, agent.getPosition(), availablePool
            )
            closestCell = dijkstraSearch(distanceMap, availablePool)

            if closestCell:
                self.agentsTargetQueue[agent.name].append(closestCell)
            else:
                # Success exploring reachable area
                self.agentTargetPool[agent.name] = []

    def recheckTargetCells(self, agent):
        if agent.brain.targetCell in [
            GridCellType.WALL.value,
            GridCellType.EXPLORED.value,
        ]:
            self.brain.targetCell = None

        for pos in self.agentsTargetQueue[agent.name]:
            if self.sharedMemory.map[pos[0], pos[1]] in [
                GridCellType.WALL.value,
                GridCellType.EXPLORED.value,
            ]:
                self.agentsTargetQueue[agent.name].remove(pos)

        for pos in self.agentTargetPool[agent.name]:
            if self.sharedMemory.map[pos[0], pos[1]] in [
                GridCellType.WALL.value,
                GridCellType.EXPLORED.value,
            ]:
                self.agentTargetPool[agent.name].remove(pos)

    def addBlockedCells(self, agent, pos):
        self.blockedCells.add(pos)
