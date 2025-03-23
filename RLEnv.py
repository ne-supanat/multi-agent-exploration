# import gym
# from gym import spaces
# import numpy as np
# import random
# from scipy.ndimage import zoom
# import math


# from environment import Environment
# from agent import Agent

# from constants.moveType import MoveType
# from constants.gridCellType import GridCellType

# # Build custom environment following guide on official gym library website
# # https://www.gymlibrary.dev/content/environment_creation/
# # Action, Observation spaces and Reward/Penalty criteria inspired by MATLAB - Train Multiple Agents for Area Coverage
# # https://uk.mathworks.com/help/reinforcement-learning/ug/train-3-agents-for-area-coverage.html


# # TODO: add document
# class GridWorldEnv(gym.Env):
#     def __init__(
#         self,
#         environment: Environment = None,
#         agent: Agent = None,
#         agents: list[Agent] = [],
#     ):
#         self.environment = environment
#         self.agent = agent
#         self.agents = agents

#         self.localMap = np.full(
#             environment.gridMap.shape,
#             GridCellType.UNEXPLORED.value,
#             dtype=int,
#         )

#         cellTypes = [type.value for type in GridCellType]

#         self.observation_space = spaces.Dict(
#             {
#                 "position": spaces.Box(
#                     low=np.array([0, 0]),  # Min values (row, column)
#                     high=np.array(
#                         [
#                             environment.gridMap.shape[0] - 1,
#                             environment.gridMap.shape[1] - 1,
#                         ]  # Max values (max row -1, max column -1)
#                     ),
#                     shape=(2,),
#                     dtype=int,
#                 ),
#                 "vision": spaces.Box(
#                     low=min(cellTypes),  # Min value within grid cell type
#                     high=max(cellTypes),  # Max value within grid cell type
#                     shape=agent.vision.shape,
#                     dtype=int,
#                 ),
#                 "local_map": spaces.Box(
#                     low=min(cellTypes),  # Min value within grid cell type
#                     high=max(cellTypes),  # Max value within grid cell type
#                     shape=environment.gridMap.shape,
#                     dtype=int,
#                 ),
#             }
#         )

#         # 5 actions, corresponding to "stay", "right", "up", "left", "down"
#         self.action_space = spaces.Discrete(len([type.value for type in MoveType]))

#         self.bonusTarget = 0.1
#         self.recentPositions = []
#         self.visitedCountLocalMap = np.zeros(environment.gridMap.shape, dtype=int)

#     def _get_obs(self):
#         # Resize local map to match trained layout shape (20x20)
#         h, w = self.localMap.shape
#         targetSize = (20, 20)
#         zoom_factors = (targetSize[0] / h, targetSize[1] / w)
#         resizedLocalMap = zoom(
#             self.localMap, zoom_factors, order=1
#         )  # order=1 = bilinear

#         return {
#             "position": self.agent.getPosition(),
#             "vision": self.getVision(),
#             "local_map": resizedLocalMap.copy(),
#         }

#     def getVision(self):
#         row, column = self.agent.getPosition()
#         halfVisionRow, halfVisionColumn = (
#             int(self.agent.vision.shape[0] // 2),  # vision shape row
#             int(self.agent.vision.shape[1] // 2),  # vision shape column
#         )
#         view = self.environment.gridMap[
#             row - halfVisionRow : row + halfVisionRow + 1,
#             column - halfVisionColumn : column + halfVisionColumn + 1,
#         ]
#         return view

#     def reset(self, seed=None, options=None):
#         # We need the following line to seed self.np_random
#         super().reset(seed=seed)

#         # Reset gridmap
#         self.environment.reset()
#         self.localMap = np.full(
#             self.environment.gridMap.shape,
#             GridCellType.UNEXPLORED.value,
#             dtype=int,
#         )

#         # Random new agent start position
#         randomPos = self.randomPosition()
#         self.agent.setPosition(randomPos[0], randomPos[1])

#         # Random new other agents start position
#         for agent in self.agents:
#             randomPos = self.randomPosition()
#             agent.setPosition(randomPos[0], randomPos[1])

#         for agent in [self.agent] + self.agents:
#             self.updateGrid(self.environment.gridMap, agent)

#         observation = self._get_obs()

#         self.bonusTarget = 0.1
#         self.recentPositions = []
#         self.visitedCountLocalMap = np.zeros(self.environment.gridMap.shape, dtype=int)

#         return observation

#     def randomPosition(self) -> int:
#         shape = self.environment.gridMap.shape
#         return (
#             random.randint(0 + 1, shape[0] - 2),  # row
#             random.randint(0 + 1, shape[1] - 2),  # column
#         )

#     def step(self, action: MoveType):
#         savedRow, savedColumn = self.agent.getPosition()
#         savedPos = (savedRow, savedColumn)

#         if action == MoveType.STAY.value:
#             self.agent.stay()
#         elif action == MoveType.UP.value:
#             self.agent.moveUp()
#         elif action == MoveType.DOWN.value:
#             self.agent.moveDown()
#         elif action == MoveType.LEFT.value:
#             self.agent.moveLeft()
#         elif action == MoveType.RIGHT.value:
#             self.agent.moveRight()

#         reward = 0

#         # Reward based on vision information
#         # TODO: consider +5 for see new partial +3 for see old partial +10 for new explored
#         # TODO: add more penalty for repetive cell more -0.1 -> -0...-10 or - more
#         visionShapeRow, visionShapeColumn = (
#             self.agent.vision.shape[0],
#             self.agent.vision.shape[1],
#         )

#         newRow, newColumn = self.agent.getPosition()

#         # agent move out of the boundary
#         if (
#             newRow <= 0
#             or newRow >= self.environment.gridMap.shape[0] - 1
#             or newColumn <= 0
#             or newColumn >= self.environment.gridMap.shape[1] - 1
#         ):
#             self.agent.setPosition(savedPos[0], savedPos[1])
#             newRow, newColumn = self.agent.getPosition()
#             reward -= 10

#         # Penalty for repeatly move in same cells in short term
#         if self.recentPositions.count((newRow, newColumn)) > 3:
#             reward -= 2

#         # Penalty for repeatly move in same cells in long term
#         reward -= (
#             self.visitedCountLocalMap[newRow, newColumn] / 100
#         )  # more visited time more penalty
#         self.visitedCountLocalMap[newRow, newColumn] += 1

#         if len(self.recentPositions) > 9:
#             self.recentPositions.pop()
#         self.recentPositions.insert(0, (newRow, newColumn))

#         # reward for vision information to encourage agent to move toward frontier cell
#         # if see partailly explored cell +1
#         # if move on partailly explored cell +5
#         for r in range(visionShapeRow):
#             for c in range(visionShapeColumn):
#                 targetRow = newRow + r - int(visionShapeRow // 2)
#                 targetColumn = newColumn + c - int(visionShapeColumn // 2)

#                 if (
#                     self.environment.gridMap[targetRow, targetColumn]
#                     == GridCellType.PARTIAL_EXPLORED.value
#                 ):
#                     reward += 1

#                 if (
#                     self.environment.gridMap[targetRow, targetColumn]
#                     == GridCellType.UNEXPLORED.value
#                 ):
#                     self.environment.gridMap[targetRow, targetColumn] = (
#                         GridCellType.PARTIAL_EXPLORED.value
#                     )
#                     reward += 5

#         # Penalty for not moving
#         if action == MoveType.STAY.value:
#             reward += -1

#         # Reward/Penalty based on where agent go
#         value = self.environment.gridMap[self.agent.getPosition()]
#         # Penalty for illegal moves (hit wall, hit other agents)
#         if value == GridCellType.WALL.value or self.agent.getPosition() in [
#             agent.getPosition() for agent in self.agents
#         ]:
#             reward += -10

#         # # Penalty for moving into already explored cell
#         # elif value == GridCellType.EXPLORED.value:
#         #     reward += -0.1
#         # Reward for moving into unexplored cell
#         elif value == GridCellType.PARTIAL_EXPLORED.value:
#             reward += 10

#         # Other agents move in random manner
#         for agent in self.agents:
#             agent.gainVisionInformation(self.environment.gridMap)
#             agent.move([self.agent] + self.agents)

#         for agent in [self.agent] + self.agents:
#             self.updateGrid(self.environment.gridMap, agent)

#         openCell = self.environment.gridMap.size - np.count_nonzero(
#             self.environment.gridMap == GridCellType.WALL.value
#         )
#         exploredCell = np.count_nonzero(
#             self.environment.gridMap == GridCellType.EXPLORED.value
#         )

#         exploredRatio = exploredCell / openCell

#         if exploredRatio > self.bonusTarget:
#             reward += 20
#             self.bonusTarget += 0.1

#         if self.environment.isFullyExplored():
#             reward += 150

#         observation = self._get_obs()

#         # An episode is done if the map is fully explored
#         terminated = self.environment.isFullyExplored()

#         return observation, reward / 100, terminated, False

#     def updateGrid(self, gridMap, agent):
#         # Update partially explored cell on gridMap
#         halfVisionRow, halfVisionColumn = (
#             int(agent.vision.shape[0] // 2),  # vision shape row
#             int(agent.vision.shape[1] // 2),  # vision shape column
#         )

#         topRow = agent.row - halfVisionRow
#         bottomRow = agent.row + halfVisionRow + 1
#         leftColumn = agent.column - halfVisionColumn
#         rightColumn = agent.column + halfVisionColumn + 1

#         visionGrid = gridMap[topRow:bottomRow, leftColumn:rightColumn]
#         visionGrid[visionGrid == GridCellType.UNEXPLORED.value] = (
#             GridCellType.PARTIAL_EXPLORED.value
#         )

#         gridMap[topRow:bottomRow, leftColumn:rightColumn] = visionGrid

#         # Update explored cell on gridMap
#         if gridMap[agent.row, agent.column] != GridCellType.WALL.value:
#             gridMap[agent.row, agent.column] = GridCellType.EXPLORED.value

#         self.localMap[topRow:bottomRow, leftColumn:rightColumn] = visionGrid

#     def render(self):
#         """Render the environment."""
#         grid = np.zeros(self.environment.gridMap.shape, dtype=str)
#         grid[:, :] = self.environment.gridMap[:, :]

#         # Mark agents
#         grid[self.agent.getPosition()] = "A"  # Label trained agent
#         for agent in self.agents:
#             grid[agent.getPosition()] = "a"  # Label other agents

#         print("\n".join([" ".join(row) for row in grid]) + "\n")
