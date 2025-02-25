import tkinter as tk
import random
from typing import List

from environment import Environment
from agent import Agent
from ticker import Ticker
from counter import Counter

from constants.experimentType import ExperimentType
from constants.layoutType import LayoutType

import environment as environment


class Experiment:
    def __init__(self):
        self.tick = 0
        self.maxTick = 100

    def runOnce(self, experimentType: ExperimentType, layoutType: LayoutType):
        window = tk.Tk()
        window.resizable(True, True)

        # Setup environment
        environment = Environment(layoutType)
        canvas = environment.createCanvas(window)
        canvas.pack()
        canvas.focus_set()

        agents = self.createAgents(canvas, experimentType, environment.cellSize)

        # Agent always explored starting point
        for agent in agents:
            environment.gridMap[agent.y, agent.x] = 2

        environment.drawGrid(canvas)

        counter = Counter()

        ticker = Ticker(canvas)
        self.update(canvas, ticker, counter, environment, agents)

        window.mainloop()

        print(f"Explored: {counter.getExploredCell()}")
        print("- experiment end -")
        return random.randint(0, 100)

    def createAgents(
        self,
        canvas: tk.Canvas,
        experimentType: ExperimentType,
        cellSize: int,
    ):
        agents = []

        # Spawn agents
        agent = Agent("A1", cellSize=cellSize)
        agent.setPosition(1, 1)
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
    ):
        gridMap = environment.gridMap

        for agent in agents:
            newX, newY = agent.update(canvas, gridMap)

            # Update explored cell on gridMap
            if gridMap[newY, newX] != 2:
                gridMap[newY, newX] = 2
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
            canvas.quit()
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
        )


if __name__ == "__main__":
    exp = Experiment()
    exp.runOnce(ExperimentType.WANDERING, LayoutType.PLAIN)
    # exp.runOnce(ExperimentType.WANDERING, LayoutType.OBSTACLES)
