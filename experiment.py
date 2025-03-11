import tkinter as tk
from typing import List

from environment import Environment
from agent import Agent, Brain
from ticker import Ticker
from counter import Counter
from centralMemory import CentralMemory

from constants.behaviourType import BehaviourType
from constants.layoutType import LayoutType
from constants.gridCellType import GridCellType

import environment as environment

from brain.brainWandering import BrainWandering
from brain.brainGreedy import BrainGreedy
from brain.brainFrontier import BrainFrontier
from brain.brainGreedyFrontier import BrainGreedyFrontier
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
        shareKnowledge=True,
    ):
        window = tk.Tk()
        window.resizable(False, False)

        # Setup environment
        environment = Environment(layoutType)
        canvas = environment.createCanvas(window)
        canvas.pack()
        canvas.focus_set()

        # Spawn agents
        agents = self.createAgents(
            canvas,
            noOfAgents,
            behaviourType,
            environment.cellSize,
            environment,
            shareKnowledge,
        )

        # Update grid map for initial stage
        gridMap = environment.gridMap
        for agent in agents:
            self.updateGrid(gridMap, agent.row, agent.column, agent)

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
        shareKnowledge: bool,
        environment: Environment = None,
    ):
        agents = []
        spawnPositions = []

        for r in range(environment.gridMap.shape[0]):
            for c in range(environment.gridMap.shape[1]):
                if environment.gridMap[r, c] != GridCellType.WALL.value:
                    spawnPositions.append((r, c))

                if len(spawnPositions) >= noOfAgents:
                    break
            if len(spawnPositions) >= noOfAgents:
                break

        maxRow, maxColumn = map(max, zip(*spawnPositions))

        if behaviourType == BehaviourType.REINFORCEMENT:
            centralMap = CentralMemory(environment.gridSize[0], environment.gridSize[1])
        elif behaviourType in [BehaviourType.FRONTIER, BehaviourType.GREEDY_FRONTIER]:
            centralMap = CentralMemory(maxColumn + 1, maxRow + 1)

        # Spawn agents
        for i in range(noOfAgents):
            agent = Agent(f"A{i}", cellSize)
            agent.setPosition(
                spawnPositions[i % len(spawnPositions)][0],
                spawnPositions[i % len(spawnPositions)][1],
            )

            if behaviourType == BehaviourType.WANDERING:
                brain = BrainWandering(agent)
            elif behaviourType == BehaviourType.GREEDY:
                brain = BrainGreedy(agent)
            elif behaviourType == BehaviourType.FRONTIER:
                if shareKnowledge:
                    centralMap = copy.deepcopy(centralMap)
                brain = BrainFrontier(agent, centralMap)
            elif behaviourType == BehaviourType.GREEDY_FRONTIER:
                if shareKnowledge:
                    centralMap = copy.deepcopy(centralMap)
                brainGreedy = BrainGreedy(agent)
                brainFrontier = BrainFrontier(agent, centralMap)
                brain = BrainGreedyFrontier(agent, brainGreedy, brainFrontier)
            elif behaviourType == BehaviourType.REINFORCEMENT:
                if shareKnowledge:
                    centralMap = copy.deepcopy(centralMap)
                brain = BrainRL(agent, environment, centralMap)
            else:
                brain = Brain(agent)
            agent.setBrain(brain)

            agents.append(agent)
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

            self.updateGrid(gridMap, newRow, newColumn, agent)

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

    def updateGrid(self, gridMap, newRow, newColumn, agent):
        # Update partially explored cell on gridMap
        halfVisionRow, halfVisionColumn = (
            int(agent.vision.shape[0] // 2),  # vision shape row
            int(agent.vision.shape[1] // 2),  # vision shape column
        )

        topRow = newRow - halfVisionRow
        bottomRow = newRow + halfVisionRow + 1
        leftColumn = newColumn - halfVisionColumn
        rightColumn = newColumn + halfVisionColumn + 1

        visionGrid = gridMap[topRow:bottomRow, leftColumn:rightColumn]
        visionGrid[visionGrid == GridCellType.UNEXPLORED.value] = (
            GridCellType.PARTIAL_EXPLORED.value
        )

        gridMap[topRow:bottomRow, leftColumn:rightColumn] = visionGrid

        # Update explored cell on gridMap
        if gridMap[newRow, newColumn] != GridCellType.WALL.value:
            gridMap[newRow, newColumn] = GridCellType.EXPLORED.value


if __name__ == "__main__":
    exp = Experiment()
    print(
        exp.runOnce(
            BehaviourType.WANDERING,
            LayoutType.DONUT_SHAPE,
            noOfAgents=10,
            shareKnowledge=True,
        )
    )
