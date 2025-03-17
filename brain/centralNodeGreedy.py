from brain.centralNode import CentralNode


class CentralNodeGreedy(CentralNode):
    # Central greedy planing: assign frontier to closest agent
    def plan(self):
        while self.sharedMemory.frontiers:
            for agent in self.agents:
                # Assign target based on order added to frontier (First in First out)
                self.agentsTargetQueue[agent.name].append(
                    self.sharedMemory.frontiers.pop(0)
                )

                if len(self.sharedMemory.frontiers) == 0:
                    break
