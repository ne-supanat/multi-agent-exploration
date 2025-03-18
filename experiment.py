import tkinter as tk
from typing import List
import random

from environment import Environment
from agent import Agent, Brain
from ticker import Ticker
from counter import Counter
from sharedMemory import SharedMemory
from brain.centralNode import CentralNode
from brain.centralNodeFrontierFIFO import CentralNodeFrontierFIFO
from brain.centralNodeFrontierGreedy import CentralNodeFrontierGreedy
from brain.centralNodeZoneSplit import CentralNodeZoneSplit


from constants.behaviourType import BehaviourType
from constants.layoutType import LayoutType
from constants.gridCellType import GridCellType

import environment as environment

from brain.brainWandering import BrainWandering
from brain.brainGreedy import BrainGreedy
from brain.brainFrontier import BrainFrontier
from brain.brainFrontierCentralised import BrainFrontierCentralised
from brain.brainGreedyFrontier import BrainGreedyFrontier
from brain.brainZoneCentralised import BrainZoneSplit
from brain.brainRL import BrainRL

import copy


class Experiment:
    def __init__(self):
        pass

    # Run experiment 1 time
    def runOnce(
        self,
        behaviourType: BehaviourType,
        layoutType: LayoutType,
        noOfAgents: int = 1,
    ):
        window = tk.Tk()
        window.resizable(False, False)
        window.lift()
        window.focus_force()

        # Setup environment
        environment = Environment(layoutType)
        canvas = environment.createCanvas(window)
        canvas.pack()
        canvas.focus_set()

        # Create central node
        # TODO: CentralNode with behaviour type (function)
        # FIFO, LIFO
        # greedy/hungarian
        # clustering
        centralNode = CentralNode([], None)

        # Spawn agents
        agents = self.createAgents(
            canvas,
            noOfAgents,
            behaviourType,
            environment.cellSize,
            environment,
            centralNode,
        )

        # Update grid map for initial stage
        gridMap = environment.gridMap
        for agent in agents:
            self.updateGrid(gridMap, agent.row, agent.column)

        environment.drawGrid(canvas)

        counter = Counter(environment.getMapSize())

        ticker = Ticker(canvas)
        self.update(canvas, ticker, counter, environment, agents, window)

        window.mainloop()

        print(f"Explored: {counter.getExploredCell()}")
        print("- experiment end -")
        return [counter.getExploredCell(), counter.getTotalMove()]

    def createAgents(
        self,
        canvas: tk.Canvas,
        noOfAgents: int,
        behaviourType: BehaviourType,
        cellSize: int,
        environment: Environment = None,
        centralNode: CentralNode = None,
    ):
        agents = []
        spawnPositions = []
        # TODO: move spawnPositions outside this function
        for r in range(environment.gridMap.shape[0]):
            for c in range(environment.gridMap.shape[1]):
                if environment.gridMap[r, c] != GridCellType.WALL.value:
                    spawnPositions.append((r, c))

        spawnPositions = random.sample(spawnPositions, noOfAgents)

        # Spawn agents
        for i in range(noOfAgents):
            agent = Agent(f"A{i}", cellSize)
            agent.setPosition(
                spawnPositions[i % len(spawnPositions)][0],
                spawnPositions[i % len(spawnPositions)][1],
            )
            agents.append(agent)

        if behaviourType in [
            BehaviourType.FRONTIER,
            BehaviourType.GREEDY_FRONTIER,
            BehaviourType.REINFORCEMENT,
            BehaviourType.FRONTIER_CENTRAL_FIFO,
            BehaviourType.FRONTIER_CENTRAL_GREEDY,
            BehaviourType.ZONE_SPLIT,
        ]:
            sharedMemory = SharedMemory(environment.gridSize)

        if behaviourType == BehaviourType.FRONTIER_CENTRAL_FIFO:
            centralNode = CentralNodeFrontierFIFO(agents, sharedMemory)
        elif behaviourType == BehaviourType.FRONTIER_CENTRAL_GREEDY:
            centralNode = CentralNodeFrontierGreedy(agents, sharedMemory)
        elif behaviourType == BehaviourType.ZONE_SPLIT:
            centralNode = CentralNodeZoneSplit(agents, sharedMemory)

        layoutShape = environment.gridMap.shape

        # Setup agent behaviour
        for agent in agents:
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

            elif behaviourType in [
                BehaviourType.FRONTIER_CENTRAL_FIFO,
                BehaviourType.FRONTIER_CENTRAL_GREEDY,
            ]:
                brain = BrainFrontierCentralised(
                    agent, layoutShape, sharedMemory, centralNode
                )
            elif behaviourType in [BehaviourType.ZONE_SPLIT]:
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
    ):
        gridMap = environment.gridMap

        for agent in agents:
            newColumn, newRow = agent.update(canvas, gridMap, agents)

            # Update explored cell counter
            if gridMap[newRow, newColumn] != GridCellType.EXPLORED.value:
                counter.explored(canvas)

            self.updateGrid(gridMap, newRow, newColumn)

        environment.drawGrid(canvas)

        counter.moved(canvas)

        # Update tick
        ticker.nextTick()
        if ticker.isReachMaxTick():  # or environment.isFullyExplored():
            window.destroy()
            return

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


if __name__ == "__main__":
    exp = Experiment()

    print(
        exp.runOnce(
            BehaviourType.ZONE_SPLIT,
            LayoutType.PLAIN,
            noOfAgents=2,
        )
    )
