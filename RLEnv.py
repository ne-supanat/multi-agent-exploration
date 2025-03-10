import gym
from gym import spaces
import numpy as np
import random

from environment import Environment
from agent import Agent

from constants.moveType import MoveType
from constants.gridCellType import GridCellType

# Build custom environment following guide on official gym library website
# https://www.gymlibrary.dev/content/environment_creation/
# Action, Observation spaces and Reward/Penalty criteria inspired by MATLAB - Train Multiple Agents for Area Coverage
# https://uk.mathworks.com/help/reinforcement-learning/ug/train-3-agents-for-area-coverage.html


# TODO: add document
# TODO: use agent local map instead
class GridWorldEnv(gym.Env):
    def __init__(
        self,
        environment: Environment = None,
        agent: Agent = None,
        agents: list[Agent] = [],
    ):
        self.environment = environment
        self.agent = agent
        self.agents = agents

        cellTypes = [type.value for type in GridCellType]

        self.observation_space = spaces.Dict(
            {
                "full_map": spaces.Box(
                    low=min(cellTypes),
                    high=max(cellTypes),
                    shape=environment.gridMap.shape,
                    dtype=int,
                ),
                "self_position": spaces.Box(
                    low=np.array([0, 0]),  # Min values (row, column)
                    high=np.array(
                        [
                            environment.gridMap.shape[0] - 1,
                            environment.gridMap.shape[1] - 1,
                        ]  # Max values (max row -1, max column -1)
                    ),
                    shape=(2,),
                    dtype=int,
                ),
                "agent_positions": spaces.Box(
                    low=np.tile(
                        np.array([0, 0]),
                        (len(self.agents), 1),
                    ),  # Min values (row, column)
                    high=np.tile(
                        np.array(
                            [
                                environment.gridMap.shape[0] - 1,
                                environment.gridMap.shape[1] - 1,
                            ]
                        ),
                        (len(self.agents), 1),
                    ),  # Max values (max row -1 , max column -1)
                    shape=(len(self.agents), 2),
                    dtype=np.int32,
                ),
            }
        )

        # 5 actions, corresponding to "stay", "right", "up", "left", "down"
        self.action_space = spaces.Discrete(len([type.value for type in MoveType]))

    def _get_obs(self):
        return {
            "full_map": self.environment.gridMap,
            "self_position": self.agent.getPosition(),
            "agent_positions": [agent.getPosition() for agent in self.agents],
        }

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        # Reset gridmap
        self.environment.reset()

        # Random new agent start position
        randomPos = self.randomPosition()
        self.agent.setPosition(randomPos[0], randomPos[1])

        # Random new other agents start position
        for agent in self.agents:
            randomPos = self.randomPosition()
            agent.setPosition(randomPos[0], randomPos[1])

        for agent in [self.agent] + self.agents:
            self.updateGrid(self.environment.gridMap, agent.row, agent.column, agent)

        observation = self._get_obs()

        return observation

    def randomPosition(self) -> int:
        shape = self.environment.gridMap.shape
        return (
            random.randint(0 + 1, shape[0] - 2),  # row
            random.randint(0 + 1, shape[1] - 2),  # column
        )

    def step(self, action: MoveType):
        savedRow, savedColumn = self.agent.getPosition()
        savedPos = (savedRow, savedColumn)

        if action == MoveType.STAY.value:
            self.agent.stay()
        elif action == MoveType.UP.value:
            self.agent.moveUp()
        elif action == MoveType.DOWN.value:
            self.agent.moveDown()
        elif action == MoveType.LEFT.value:
            self.agent.moveLeft()
        elif action == MoveType.RIGHT.value:
            self.agent.moveRight()

        reward = 0

        # Reward based on vision information
        visionShapeRow, visionShapeColumn = (
            self.agent.vision.shape[0],
            self.agent.vision.shape[1],
        )

        newRow, newColumn = self.agent.getPosition()

        if (
            newRow <= 0
            or newRow >= self.environment.gridMap.shape[0] - 1
            or newColumn <= 0
            or newColumn >= self.environment.gridMap.shape[1] - 1
        ):  # agent move out of boundary
            self.agent.setPosition(savedPos[0], savedPos[1])
            newRow, newColumn = self.agent.getPosition()
            reward -= 50

        for r in range(visionShapeRow):
            for c in range(visionShapeColumn):
                targetRow = newRow + r - int(visionShapeRow // 2)
                targetColumn = newColumn + c - int(visionShapeColumn // 2)

                if (
                    self.environment.gridMap[targetRow, targetColumn]
                    == GridCellType.UNEXPLORED.value
                ):
                    self.environment.gridMap[targetRow, targetColumn] = (
                        GridCellType.PARTIAL_EXPLORED.value
                    )
                    reward += 1

        # Penalty for not moving
        if action == MoveType.STAY.value:
            reward += -1

        # Reward/Penalty based on where agent go
        value = self.environment.gridMap[self.agent.getPosition()]
        # Penalty for illegal moves (hit wall, hit other agents)
        if value == GridCellType.WALL.value or self.agent.getPosition() in [
            agent.getPosition() for agent in self.agents
        ]:
            reward += -10
        # Penalty for moving into already explored cell
        elif value == GridCellType.EXPLORED.value:
            reward += -0.5
        # Reward for moving into unexplored cell
        elif value == GridCellType.PARTIAL_EXPLORED.value:
            reward += 2

        self.updateGrid(
            self.environment.gridMap, self.agent.row, self.agent.column, self.agent
        )

        if self.environment.isFullyExplored():
            reward += 100

        observation = self._get_obs()

        # An episode is done if the map is fully explored
        terminated = self.environment.isFullyExplored()

        return observation, reward, terminated, False

    def updateGrid(self, gridMap, newRow, newColumn, agent):
        # Update explored cell on gridMap
        if gridMap[newRow, newColumn] != GridCellType.WALL.value:
            gridMap[newRow, newColumn] = GridCellType.EXPLORED.value

        # Update partially explored cell on gridMap
        visionShapeRow, visionShapeColumn = (
            agent.vision.shape[0],
            agent.vision.shape[1],
        )
        for r in range(visionShapeRow):
            for c in range(visionShapeColumn):
                targetRow = newRow + r - int(visionShapeRow // 2)
                targetColumn = newColumn + c - int(visionShapeColumn // 2)

                if (
                    targetRow < 0
                    or targetRow >= self.environment.gridMap.shape[0]
                    or targetColumn < 0
                    or targetColumn >= self.environment.gridMap.shape[1]
                ):  # target row, column are within map
                    continue

                if gridMap[targetRow, targetColumn] == GridCellType.UNEXPLORED.value:
                    gridMap[targetRow, targetColumn] = (
                        GridCellType.PARTIAL_EXPLORED.value
                    )

    def render(self):
        """Render the environment."""
        grid = np.zeros(self.environment.gridMap.shape, dtype=str)
        grid[:, :] = self.environment.gridMap[:, :]

        # Mark agents
        grid[self.agent.getPosition()] = "A"  # Label trained agent
        for agent in self.agents:
            grid[agent.getPosition()] = "a"  # Label other agents

        print("\n".join([" ".join(row) for row in grid]) + "\n")


from gym.envs.registration import register


if __name__ == "__main__":
    print("regist env")

    register(
        id="gym_examples/GridWorld-v0",
        entry_point="gym_examples.envs:GridWorldEnv",
        max_episode_steps=20,
    )
