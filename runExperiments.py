from experiment import Experiment
import pandas as pd
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
from itertools import combinations
import random

from cw.constants.behaviourType import BehaviourType
from constants.layoutType import LayoutType


# This file is a modification of university of nottingham COMP4105 24-25 module's material

NO_OF_REPS = 3


# Run experiment for several times
# noOfReps: number of repetition time
def runMultipleExperiments(noOfReps: int, behaviourType: BehaviourType):
    results = []
    for _ in range(noOfReps):
        exp = Experiment()
        results.append(exp.runOnce(behaviourType, LayoutType.PLAIN))
    return results


# Run all type of experiment for several times
def runExperimentsWithDifferentParameters():
    experiments = [
        BehaviourType.WANDERING,
        BehaviourType.FRONTIER,
        BehaviourType.REINFORCEMENT,
    ]

    resultsTable = {}

    # run experiment 10 times for each type
    for experiment in experiments:
        dirtCollectedList = runMultipleExperiments(NO_OF_REPS, experiment)
        resultsTable[experiment] = dirtCollectedList

    ## create exel file from experiment results
    # print(resultsTable)
    results = pd.DataFrame(resultsTable)
    # print(results)
    # results.to_excel("cw/experiments.xlsx")

    # Show each experiment type mean
    for result in results:
        print(f"{result} mean: {results[result].mean(axis=0)}")

    # results.boxplot(grid=False)
    # plt.show()

    # Conduct statistical test of pair of experiments
    # using combinations to create all possible pairs that not repeat it self
    # https://www.geeksforgeeks.org/python-all-possible-pairs-in-list/
    for pair in list(combinations(experiments, 2)):
        experiment1 = pair[0]
        experiment2 = pair[1]

        print(f"{experiment1}, {experiment2}:")
        print(f"{ttest_ind(results[experiment1], results[experiment2])}")


runExperimentsWithDifferentParameters()
