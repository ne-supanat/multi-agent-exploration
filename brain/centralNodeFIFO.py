from brain.centralNode import CentralNode


class CentralNodeFIFO(CentralNode):
    # Central FIFO planing: assign target based on order added to frontier (First in First out)
    def planAll(self):
        while self.sharedMemory.frontiers:
            for agent in self.agents:
                self.agentsTargetQueue[agent.name].append(
                    self.sharedMemory.frontiers.pop(0)
                )

                if len(self.sharedMemory.frontiers) == 0:
                    break

    # Planing a sequence of target for one agent
    def planOne(self, agent):
        self.planAll()
