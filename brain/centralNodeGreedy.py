from brain.centralNode import CentralNode


class CentralNodeGreedy(CentralNode):
    # Central greedy planing: assign frontier to closest agent
    def planAll(self):
        for agent in self.agents:
            self.findCloestFrontier(agent)

    # Planing a sequence of target for one agent
    def planOne(self, agent):
        self.findCloestFrontier(agent)

    def findCloestFrontier(self, agent):
        if len(self.sharedMemory.frontiers) > 0:
            closestFrontier = None
            closestDistance = float("inf")

            for frontier in self.sharedMemory.frontiers:
                print(frontier)
                fronteirRow, fronteirColumn = frontier

                distance = abs(fronteirRow - agent.row) + abs(
                    fronteirColumn - agent.column
                )

                if distance < closestDistance:
                    closestDistance = distance
                    closestFrontier = frontier

            self.agentsTargetQueue[agent.name].append(closestFrontier)
            self.sharedMemory.frontiers.remove(closestFrontier)
