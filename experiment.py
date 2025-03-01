import tkinter as tk
import random
from typing import List

from environment import Environment
from agent import Agent
from ticker import Ticker
from counter import Counter

from constants.behaviourType import BehaviourType
from constants.layoutType import LayoutType
from constants.gridCellType import GridCellType

import environment as environment


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

        # Agent always explored starting point
        for agent in agents:
            environment.gridMap[agent.y, agent.x] = GridCellType.EXPLORED.value

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
        pos = [(1, 1)]

        # Spawn agents
        for i in range(noOfAgents):
            agent = Agent(f"A{i}", cellSize, behaviourType)
            agent.setPosition(pos[i % len(pos)][0], pos[i % len(pos)][1])
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
            newX, newY = agent.update(canvas, gridMap, agents)

            # Update explored cell on gridMap
            if gridMap[newY, newX] != GridCellType.EXPLORED.value:
                gridMap[newY, newX] = GridCellType.EXPLORED.value
                counter.explored(canvas)

            # Update partially explored cell on gridMap
            visionShapeRow, visionShapeColumn = (
                agent.vision.shape[0],
                agent.vision.shape[1],
            )
            for r in range(visionShapeRow):
                for c in range(visionShapeColumn):
                    targetY = newY + r - int(visionShapeRow // 2)
                    targetX = newX + c - int(visionShapeColumn // 2)

                    if gridMap[targetY, targetX] == GridCellType.UNEXPLORED.value:
                        gridMap[targetY, targetX] = GridCellType.PARTIAL_EXPLORED.value

        environment.drawGrid(canvas)

        counter.moved(canvas)

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
    # exp.runOnce(BehaviourType.FRONTIER, LayoutType.OBSTACLES)
    exp.runOnce(BehaviourType.WANDERING, LayoutType.PLAIN, noOfAgents=1)
