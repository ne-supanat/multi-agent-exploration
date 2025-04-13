import math
from scipy.optimize import linear_sum_assignment
import numpy as np

from brain.centralNode import CentralNode
from sharedMemory import SharedMemory

from constants.gridCellType import GridCellType


from dijkstraMap import dijkstraMap, dijkstraSearch


class CentralNodeZoneVoronoi(CentralNode):
    def __init__(self, agents, sharedMemory, canvas=None, cellSize=20, dynamic=True):
        super().__init__(agents, sharedMemory)

        self.canvas = canvas
        self.cellSize = cellSize
        self.dynamic = dynamic

        self.agentTargetPool = {}

        for agent in self.agents:
            self.agentsTargetQueue[agent.name] = []

        self.planAll()

    # Central voronoi planing: assign zone
    def planAll(self):
        for agent in self.agents:
            self.agentTargetPool[agent.name] = []

        self.canvas.delete("voronoi")
        shape = self.sharedMemory.map.shape

        distanceMaps = {}
        for agent in self.agents:
            distanceMaps[agent.name] = dijkstraMap(
                self.sharedMemory.map, agent.getPosition()
            )

        for row in range(shape[0]):
            for column in range(shape[1]):
                if self.sharedMemory.map[row, column] in [GridCellType.WALL.value]:
                    continue

                bestAgent = None
                minDistance = float("inf")

                for agent in self.agents:
                    distance = distanceMaps[agent.name][row, column]

                    if distance < minDistance:
                        minDistance = distance
                        bestAgent = agent

                if bestAgent:
                    if self.sharedMemory.map[row, column] not in [
                        GridCellType.WALL.value,
                        GridCellType.EXPLORED.value,
                    ]:
                        self.agentTargetPool[bestAgent.name].append((row, column))

                    # Mark area on map
                    x1, y1 = column * self.cellSize, row * self.cellSize
                    x2, y2 = x1 + self.cellSize, y1 + self.cellSize
                    self.canvas.create_rectangle(
                        x1,
                        y1,
                        x2,
                        y2,
                        # fill=bestAgent.colour,
                        outline=bestAgent.colour,
                        width=2,
                        tags="voronoi",
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

    def recheckTargetQueues(self, agent):
        for agent in self.agents:
            for pos in self.agentsTargetQueue[agent.name]:
                if self.sharedMemory.map[pos[0], pos[1]] in [
                    GridCellType.WALL.value,
                    GridCellType.EXPLORED.value,
                ]:
                    self.agentsTargetQueue[agent.name].remove(pos)
