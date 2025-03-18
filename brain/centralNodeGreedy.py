from brain.centralNode import CentralNode

from dijkstraMap import dijkstraMap, dijkstraSearch


class CentralNodeGreedy(CentralNode):
    # Central greedy planing: assign frontier to closest agent
    def planAll(self):
        for agent in self.agents:
            self.findClosestFrontier(agent)

    # Planing a sequence of target for one agent
    def planOne(self, agent):
        self.findClosestFrontier(agent)

    def findClosestFrontier(self, agent):
        if len(self.sharedMemory.frontiers) > 0:
            distanceMap = dijkstraMap(self.sharedMemory.map, agent.getPosition())
            closestFrontier = dijkstraSearch(distanceMap, self.sharedMemory.frontiers)

            self.agentsTargetQueue[agent.name].append(closestFrontier)
            self.sharedMemory.frontiers.remove(closestFrontier)
