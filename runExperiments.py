import csv
from experiment import Experiment
from environment import Environment
import pandas as pd
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
from itertools import combinations
import random

from constants.behaviourType import BehaviourType
from constants.layoutType import LayoutType


# This file is a modification of university of nottingham COMP4105 24-25 module's material

# Number of total experiment run
# NOTE: this number calulated and selected using cumulative means from Frontier behaviour in Plain layout experiment runs)
NO_OF_REPS = 40


# Run all type of experiment for several times
def runExperimentsWithDifferentParameters():
    layouts = [
        LayoutType.PLAIN,
        LayoutType.RL_PLAIN_SM,
    ]  # [layout for layout in LayoutType]
    behaviours = [
        BehaviourType.FRONTIER,
        BehaviourType.GREEDY_FRONTIER,
    ]  # [behaviour for behaviour in BehaviourType]
    numOfAgents = [2]  # [2, 5, 10]

    # run experiment NO_OF_REPS times
    for numOfAgent in numOfAgents:
        for layout in layouts:
            savedPath = (
                f"cw/experimentResults/experiment_{layout.name}_{numOfAgent}.csv"
            )
            with open(savedPath, mode="w", newline="") as file:
                writer = csv.writer(file)

                writer.writerow(
                    ["Behaviour", "Round", "total100", "total90", "total75", "total50"]
                )

            for round in range(NO_OF_REPS):
                exp = Experiment()
                env = Environment(layout)
                spawnPositions = exp.generateSpawnPositions(env, numOfAgent)

                for behaviour in behaviours:
                    # =======
                    # Format in each LAYOUT ROUND
                    # BEHAVIOUR  ROUND  TOTAL100  TOTAL90  TOTAL75  TOTAL50
                    # Wandering  1      100       90       75       50
                    # =======

                    result = exp.runOnce(
                        behaviourType=behaviour,
                        environment=env,
                        noOfAgents=numOfAgent,
                        spawnPositions=spawnPositions,
                    )

                    print(f"{layout.name}-{behaviour.name} {round}: {result}")

                    with open(savedPath, mode="a", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerow([behaviour.name, round] + result)


runExperimentsWithDifferentParameters()
