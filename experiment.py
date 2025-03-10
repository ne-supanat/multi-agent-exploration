import tkinter as tk
from typing import List

from environment import Environment
from agent import Agent, Brain
from ticker import Ticker
from counter import Counter
from centralMemory import CentralMap

from constants.behaviourType import BehaviourType
from constants.layoutType import LayoutType
from constants.gridCellType import GridCellType

import environment as environment

from brain.brainWandering import BrainWandering
from brain.brainGreedy import BrainGreedy
from brain.brainFrontier import BrainFrontier
from brain.brainRL import BrainRL


class Experiment:
    def __init__(self):
        pass

    # Run experiment 1 time
    def runOnce(
        self, behaviourType: BehaviourType, layoutType: LayoutType, noOfAgents: int = 1
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
            canvas, noOfAgents, behaviourType, environment.cellSize
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
    ):
        agents = []
        # pos = [(1, 1), (1, 2), (1, 3), (1, 4)]  # row, column
        pos = [(1, 1), (1, 2), (2, 1)]  # row, column

        maxRow, maxColumn = map(max, zip(*pos))
        centralMap = CentralMap(maxColumn + 1, maxRow + 1)
        # centralMap = CentralMap(10, 10)

        # Spawn agents
        for i in range(noOfAgents):
            agent = Agent(f"A{i}", cellSize)
            agent.setPosition(pos[i % len(pos)][0], pos[i % len(pos)][1])

            if behaviourType == BehaviourType.WANDERING:
                brain = BrainWandering(agent)
            elif behaviourType == BehaviourType.GREEDY:
                brain = BrainGreedy(agent)
            elif behaviourType == BehaviourType.FRONTIER:
                brain = BrainFrontier(agent, centralMap)
            elif behaviourType == BehaviourType.REINFORCEMENT:
                brain = BrainRL(agent)
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
                    or targetRow > gridMap.shape[0]
                    or targetColumn < 0
                    or targetColumn > gridMap.shape[1]
                ):
                    continue

                if gridMap[targetRow, targetColumn] == GridCellType.UNEXPLORED.value:
                    gridMap[targetRow, targetColumn] = (
                        GridCellType.PARTIAL_EXPLORED.value
                    )


if __name__ == "__main__":
    exp = Experiment()
    # exp.runOnce(BehaviourType.FRONTIER, LayoutType.OBSTACLES)
    print(exp.runOnce(BehaviourType.REINFORCEMENT, LayoutType.PLAIN, noOfAgents=1))
    # exp.runOnce(BehaviourType.FRONTIER, LayoutType.OBSTACLES, noOfAgents=1)
