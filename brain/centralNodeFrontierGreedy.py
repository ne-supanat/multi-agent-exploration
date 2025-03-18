from brain.centralNode import CentralNode

from dijkstraMap import dijkstraMap, dijkstraSearch


class CentralNodeFrontierGreedy(CentralNode):
    def __init__(self, agents, sharedMemory):
        super().__init__(agents, sharedMemory)
        self.initialised = False

    # Collect initial frontier cell position
    def gatheringInfo(self, agent):
        # Prepare field
        self.agentsTargetQueue[agent.name] = []

        # Central node will be ready after gather all information form all agents
        self.initialised = len(self.agentsTargetQueue) == len(self.agents)

        # After gather all information start planing
        if self.initialised:
            self.planAll()

    # Central greedy planing: assign frontier to closest agent
    def planAll(self):
        for agent in self.agents:
            self.findClosestFrontier(agent)
            self.sharedMemory.signUpOnTask(
                agent.name, self.agentsTargetQueue[agent.name].pop(0)
            )

    # Planing a sequence of target for one agent
    def planOne(self, agent):
        self.findClosestFrontier(agent)

    def findClosestFrontier(self, agent):
        if len(self.sharedMemory.frontiers) > 0:
            distanceMap = dijkstraMap(self.sharedMemory.map, agent.getPosition())
            closestFrontier = dijkstraSearch(distanceMap, self.sharedMemory.frontiers)

            self.agentsTargetQueue[agent.name].append(closestFrontier)
            self.sharedMemory.frontiers.remove(closestFrontier)
