from brain.centralNode import CentralNode


class CentralNodeFrontierFIFO(CentralNode):
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

    # Central FIFO planing: assign target based on order added to frontier (First in First out)
    def planAll(self):
        self.plan()
        for agent in self.agents:
            if self.agentsTargetQueue[agent.name]:
                self.sharedMemory.signUpOnTask(
                    agent.name, self.agentsTargetQueue[agent.name].pop(0)
                )

    # Planing a sequence of target for one agent
    def planOne(self, agent):
        self.plan()

    def plan(self):
        while self.sharedMemory.frontiers:
            for agent in self.agents:
                self.agentsTargetQueue[agent.name].append(
                    self.sharedMemory.frontiers.pop(0)
                )

                if len(self.sharedMemory.frontiers) == 0:
                    break
