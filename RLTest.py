import numpy as np
import random

from agent import Agent
from environment import Environment
from RLEnv import GridWorldEnv

from constants.layoutType import LayoutType
from constants.moveType import MoveType

environment = Environment(LayoutType.TEST)
env = GridWorldEnv(
    environment=environment,
    agent=Agent("A0", environment.cellSize),
    agents=[],
)

obs = env.reset()
env.render()

for i in range(2):
    action = MoveType.DOWN
    obs, rewards, done, _ = env.step(action)

    env.render()
    print("Rewards:", rewards)
    print("Observation", obs)
