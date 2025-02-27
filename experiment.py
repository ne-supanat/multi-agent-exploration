import tkinter as tk
import random
from typing import List

from environment import Environment
from agent import Agent
from ticker import Ticker
from counter import Counter

from constants.experimentType import ExperimentType
from constants.layoutType import LayoutType
from constants.gridCellType import GridCellType

import environment as environment


class Experiment:
    def __init__(self):
        pass

    # Run experiment 1 time
    def runOnce(self, experimentType: ExperimentType, layoutType: LayoutType):
        window = tk.Tk()
        window.resizable(True, True)

        # Setup environment
        environment = Environment(layoutType)
        canvas = environment.createCanvas(window)
        canvas.pack()
        canvas.focus_set()

        # Spawn agents
        agents = self.createAgents(canvas, 2, experimentType, environment.cellSize)

        # Agent always explored starting point
        for agent in agents:
            environment.gridMap[agent.y, agent.x] = GridCellType.EXPLORED.value

        environment.drawGrid(canvas)

        counter = Counter()

        ticker = Ticker(canvas)
        self.update(canvas, ticker, counter, environment, agents, window)

        window.mainloop()

        print(f"Explored: {counter.getExploredCell()}")
        print("- experiment end -")
        return counter.getExploredCell()

    def createAgents(
        self,
        canvas: tk.Canvas,
        noOfAgents: int,
        experimentType: ExperimentType,
        cellSize: int,
    ):
        agents = []
        pos = [(1, 1), (1, 2)]

        # Spawn agents
        for i in range(noOfAgents):
            agent = Agent(f"A{i}", cellSize=cellSize)
            agent.setPosition(pos[i][0], pos[i][1])
            # brain = Brain(bot, expWandering)
            # bot.setBrain(brain)
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
            newX, newY = agent.update(canvas, gridMap)

            # Update explored cell on gridMap
            if gridMap[newY, newX] != GridCellType.EXPLORED.value:
                gridMap[newY, newX] = GridCellType.EXPLORED.value
                counter.explored(canvas)

            # Update partially explored cell on gridMap
            for r in range(3):
                for c in range(3):
                    targetY = newY + r - 1
                    targetX = newX + c - 1

                    if gridMap[targetY, targetX] == 0:
                        gridMap[targetY, targetX] = 1

        environment.drawGrid(canvas)

        # Update tick
        ticker.nextTick()
        if ticker.isReachMaxTick():
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


if __name__ == "__main__":
    exp = Experiment()
    exp.runOnce(ExperimentType.WANDERING, LayoutType.OBSTACLES)
    # exp.runOnce(ExperimentType.WANDERING, LayoutType.OBSTACLES)
