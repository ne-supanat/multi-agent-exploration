from environment import Environment

# This file is a modification of university of nottingham COMP4105 24-25 module's material


class Counter:
    def __init__(self, mapSize):
        self.totalMove = 0
        self.mapSize = mapSize

    def updateMovementCounter(self, canvas):
        self.totalMove += 1
        canvas.delete("totalMoveCount")

        # Total number of explored cell / open cell
        # format: "Moved: 0"
        canvas.create_text(
            10,
            self.mapSize[0] + 15,
            anchor="w",
            text="Moved: " + str(self.totalMove),
            tags="totalMoveCount",
        )

    def updateExplorationCounter(self, canvas, environment: Environment):
        canvas.delete("exploredCellCount")

        # Total number of explored cell / open cell
        # format: "Explored: 100/100"
        canvas.create_text(
            10,
            self.mapSize[0] + 30,
            anchor="w",
            text=f"Explored: {environment.totalCellExplored()}/{environment.totalCellOpen()}",
            tags="exploredCellCount",
        )

        # Current coverage %
        # format: "Coverage: 100.00%"
        canvas.create_text(
            10,
            self.mapSize[0] + 45,
            anchor="w",
            text=f"Coverage: {environment.currentCoverage():.2f}%",
            tags="exploredCellCount",
        )

    def getTotalMove(self):
        return self.totalMove
