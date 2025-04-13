import tkinter as tk
from typing import List
import random
import numpy as np
import matplotlib as mpl


from environment import Environment
from agent import Agent, Brain
from ticker import Ticker
from counter import Counter
from sharedMemory import SharedMemory
from brain.centralNode import CentralNode
from brain.centralNodeFrontierFIFO import CentralNodeFrontierFIFO
from brain.centralNodeFrontierGreedy import CentralNodeFrontierGreedy
from brain.centralNodeZoneSplit import CentralNodeZoneSplit
from brain.centralNodeZoneVoronoi import CentralNodeZoneVoronoi


from constants.behaviourType import BehaviourType
from constants.layoutType import LayoutType
from constants.gridCellType import GridCellType

import environment as environment

from brain.brainWandering import BrainWandering
from brain.brainGreedy import BrainGreedy
from brain.brainFrontier import BrainFrontier
from brain.brainFrontierAssist import BrainFrontierAssist
from brain.brainFrontierCentralised import BrainFrontierCentralised
from brain.brainGreedyFrontier import BrainGreedyFrontier
from brain.brainZoneCentralised import BrainZoneSplit
from brain.brainScout import BrainScout

# from brain.brainRL import BrainRL

import copy


class Experiment:
    def __init__(self):
        pass

    # Run experiment 1 time
    def runOnce(
        self,
        behaviourType: BehaviourType,
        environment: Environment,
        noOfAgents: int = 1,
        spawnPositions=[],
        showHeatmap=False,
    ):
        window = tk.Tk()
        window.resizable(False, False)
        window.lift()
        window.focus_force()

        # Setup environment
        canvas = tk.Canvas(
            window,
            # width = content width + heatmap width
            width=(
                environment.gridSize[1]
                * environment.cellSize
                * (2 if showHeatmap else 1)
            ),
            # height = content height + space(10) + (number of conter item * text component height(15))
            height=environment.gridSize[0] * environment.cellSize + 10 + (3 * 15),
        )

        canvas.pack()
        canvas.focus_set()

        # Create central node
        centralNode = CentralNode([], None)

        # Spawn agents
        agents = self.createAgents(
            canvas,
            noOfAgents,
            behaviourType,
            environment.cellSize,
            environment,
            centralNode,
            spawnPositions,
            showHeatmap,
        )

        # Update grid map for initial stage
        gridMap = environment.gridMap
        for agent in agents:
            self.updateGrid(gridMap, agent.row, agent.column)

        environment.drawGridVisualBase(canvas)
        if showHeatmap:
            environment.drawGridHeatmapInfo(canvas)
            environment.drawGridHeatmapBase(canvas)

        counter = Counter(environment.getMapSize())

        ticker = Ticker(canvas)
        self.update(canvas, ticker, counter, environment, agents, window, showHeatmap)

        window.mainloop()

        # Return experimental data
        return counter.getExperimenterResult()

    def createAgents(
        self,
        canvas: tk.Canvas,
        noOfAgents: int,
        behaviourType: BehaviourType,
        cellSize: int,
        environment: Environment = None,
        centralNode: CentralNode = None,
        spawnPositions=[],
        showHeatmap=False,
    ):
        # canvas.create_oval
        agentColours = [
            "blue",
            "red",
            "orange",
            "yellow",
            "green",
            "violet",
            "black",
            "white",
            "cornflower blue",
            "indian red",
        ]
        agents = []

        # Spawn agents
        for i in range(noOfAgents):
            agent = Agent(
                f"A{i}",
                cellSize,
                colour=agentColours[i % len(agentColours)],
                showHeatmap=showHeatmap,
            )
            agent.setPosition(
                spawnPositions[i % len(spawnPositions)][0],
                spawnPositions[i % len(spawnPositions)][1],
            )
            agents.append(agent)

        sharedMemory = SharedMemory(environment.gridSize)

        if behaviourType == BehaviourType.FRONTIER_CENTRAL_FIFO:
            centralNode = CentralNodeFrontierFIFO(agents, sharedMemory)
        elif behaviourType == BehaviourType.FRONTIER_CENTRAL_GREEDY:
            centralNode = CentralNodeFrontierGreedy(agents, sharedMemory)
        elif behaviourType == BehaviourType.ZONE_SPLIT:
            centralNode = CentralNodeZoneSplit(agents, sharedMemory)
        elif behaviourType == BehaviourType.ZONE_VORONOI:
            centralNode = CentralNodeZoneVoronoi(agents, sharedMemory, canvas, cellSize)

        layoutShape = environment.gridMap.shape

        # Setup agent behaviour
        for i, agent in enumerate(agents):
            if behaviourType == BehaviourType.WANDERING:
                brain = BrainWandering(agent, layoutShape)
            elif behaviourType == BehaviourType.GREEDY:
                brain = BrainGreedy(agent, layoutShape)
            elif behaviourType == BehaviourType.FRONTIER:
                brain = BrainFrontier(agent, layoutShape, sharedMemory)
            elif behaviourType == BehaviourType.GREEDY_FRONTIER:
                brainGreedy = BrainGreedy(agent, layoutShape)
                brainFrontier = BrainFrontier(agent, layoutShape, sharedMemory)
                brain = BrainGreedyFrontier(
                    agent, layoutShape, brainGreedy, brainFrontier
                )
            elif behaviourType == BehaviourType.FRONTIER_ASSIST:
                brain = BrainFrontierAssist(agent, layoutShape, sharedMemory)
            elif behaviourType == BehaviourType.SCOUT:
                # 1 in 3 agents will be in scout role
                if i / noOfAgents < 0.30:
                    brain = BrainScout(agent, layoutShape, sharedMemory)
                else:
                    brain = BrainFrontier(agent, layoutShape, sharedMemory)
            elif behaviourType in [
                BehaviourType.FRONTIER_CENTRAL_FIFO,
                BehaviourType.FRONTIER_CENTRAL_GREEDY,
            ]:
                brain = BrainFrontierCentralised(
                    agent, layoutShape, sharedMemory, centralNode
                )
            elif behaviourType in [
                BehaviourType.ZONE_SPLIT,
                BehaviourType.ZONE_VORONOI,
            ]:
                brain = BrainZoneSplit(agent, layoutShape, centralNode)

            # elif behaviourType == BehaviourType.REINFORCEMENT:
            #     # not sharing knowledge: each agent have its own version of central map
            #     if not shareKnowledge:
            #         centralMap = copy.deepcopy(centralMap)
            #     brain = BrainRL(agent, environment, centralMap)
            else:
                brain = Brain(agent, layoutShape)
            agent.setBrain(brain)
            agent.draw(canvas)

        return agents

    def update(
        self,
        canvas: tk.Canvas,
        ticker: Ticker,
        counter: Counter,
        environment: Environment,
        agents: List[Agent],
        window: tk.Tk,
        showHeatmap=False,
    ):
        # End experiment if reach maximum moves or complete the exploration
        if ticker.isReachMaxTick() or environment.isFullyExplored():
            window.destroy()
            return

        gridMap = environment.gridMap
        accumulatedGridmap = np.zeros(gridMap.shape, dtype=int)

        for agent in agents:
            newColumn, newRow = agent.update(canvas, gridMap, agents)
            self.updateGrid(gridMap, newRow, newColumn)
            accumulatedGridmap += agent.brain.visitedMap

        environment.updateGridVisual(canvas)
        if showHeatmap:
            environment.updateGridHeatmap(canvas, accumulatedGridmap)

        counter.updateExplorationCounter(canvas, environment)

        counter.updateMovementCounter(canvas)

        # Update tick
        ticker.nextTick()

        # update after frame after specific milliseconds
        canvas.after(
            ticker.getTickSpeed(),
            self.update,
            canvas,
            ticker,
            counter,
            environment,
            agents,
            window,
            showHeatmap,
        )

    def updateGrid(self, gridMap, newRow, newColumn):
        # Update partially explored cell on gridMap
        visionGrid = gridMap[newRow - 1 : newRow + 2, newColumn - 1 : newColumn + 2]
        visionGrid[visionGrid == GridCellType.UNEXPLORED.value] = (
            GridCellType.PARTIAL_EXPLORED.value
        )

        gridMap[newRow - 1 : newRow + 2, newColumn - 1 : newColumn + 2] = visionGrid

        # Update explored cell on gridMap
        if gridMap[newRow, newColumn] != GridCellType.WALL.value:
            gridMap[newRow, newColumn] = GridCellType.EXPLORED.value

    def generateSpawnPositions(self, environment: Environment, noOfAgents=1):
        spawnPositions = []
        for r in range(environment.gridMap.shape[0]):
            for c in range(environment.gridMap.shape[1]):
                if environment.gridMap[r, c] != GridCellType.WALL.value:
                    spawnPositions.append((r, c))

        return random.sample(spawnPositions, noOfAgents)


if __name__ == "__main__":
    exp = Experiment()

    noOfAgents = 5
    # behaviour = BehaviourType.WANDERING
    behaviour = BehaviourType.ZONE_VORONOI
    env = Environment(LayoutType.HOUSE)
    spawnPositions = exp.generateSpawnPositions(env, noOfAgents)
    # spawnPositions = [(3, 5), (23, 23)]

    print(
        exp.runOnce(
            behaviourType=behaviour,
            environment=env,
            noOfAgents=noOfAgents,
            spawnPositions=spawnPositions,
            showHeatmap=False,
        )
    )
