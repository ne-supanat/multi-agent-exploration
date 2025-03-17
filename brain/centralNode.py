from scipy.optimize import linear_sum_assignment
import numpy as np

from constants.gridCellType import GridCellType
from sharedMemory import SharedMemory


class CentralNode:
    def __init__(self, agents, sharedMemory: SharedMemory):
        self.initialised = False
        self.agents = agents
        self.sharedMemory = sharedMemory

        self.agentsTargetQueue = {}  # {agentName: [ (row,column) ]}

    def gatheringInfo(self, agent):
        # Prepare field
        self.agentsTargetQueue[agent.name] = []

        # Central node will be ready after gather all information form all agents
        self.initialised = len(self.agentsTargetQueue) == len(self.agents)

        # After gather all information start planing
        if self.initialised:
            self.plan()
            for agent in self.agents:
                if self.agentsTargetQueue[agent.name]:
                    self.sharedMemory.signUpOnTask(
                        agent.name, self.agentsTargetQueue[agent.name].pop(0)
                    )

    # Planing a sequence of target for agent
    def plan(self):
        pass

    # Return next agent's target or planing new sequence of target for agent
    def getNextTarget(self, agentName):
        if self.agentsTargetQueue[agentName]:
            return self.agentsTargetQueue[agentName].pop(0)
        else:
            self.plan()
            if self.agentsTargetQueue[agentName]:
                return self.getNextTarget(agentName)
            else:
                return None


# # Create distance matrix of each agent to each cell
# distanceMatrix = np.zeros((len(self.agents), len(self.sharedMemory.frontiers)))

# for i, agent in enumerate(self.agents):
#     for j, frontier in enumerate(self.sharedMemory.frontiers):
#         distanceMatrix[i, j] = abs(frontier[0] - agent.row) + abs(
#             frontier[1] - agent.column
#         )

# # Find the closest frontier for each agent
# # using assignment problem optimisation method
# # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html
# rowIndex, columnIndex = linear_sum_assignment(distanceMatrix)

# for i in rowIndex:
#     targetCell = self.sharedMemory.frontiers[columnIndex[i]]
#     self.agentsTargetQueue[self.agents[i].name] = [targetCell]

#     self.sharedMemory.removeFrontier(targetCell)

# # Chaining assignment
# # assign cloest frontier from last assigned
# # for agent in self.agents:

# for agent in self.agents:
#     # Compute distances from this agent to all frontiers
#     distances = [
#         abs(frontier[0] - self.agent.row) + abs(frontier[1] - self.agent.column)
#         for frontier in self.sharedMemory.frontiers
#     ]
#     # Get the closest frontier
#     min_index = np.argmin(distances)
#     closestFrontier = self.sharedMemory.frontiers[min_index]

# # for frontier in self.sharedMemory.frontiers:
# #     fronteirRow, fronteirColumn = frontier

# #     # Manhattan distance
# #     distance = abs(fronteirRow - self.agent.row) + abs(
# #         fronteirColumn - self.agent.column
# #     )

# #     if distance < closestDistance:
# #         closestDistance = distance
# #         closestFrontier = frontier

# # self.targetCell = closestFrontier
# # self.planNewPath()
