from environment import Environment

# This file is a modification of university of nottingham COMP4105 24-25 module's material


class Counter:
    def __init__(self, mapSize):
        self.totalMove = 0

        self.total50 = -1
        self.total75 = -1
        self.total90 = -1
        self.total100 = -1

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

        if self.total100 and environment.currentCoverage() >= 100:
            self.total100 = self.totalMove
        elif self.total90 and environment.currentCoverage() >= 90:
            self.total90 = self.totalMove
        elif self.total75 and environment.currentCoverage() >= 75:
            self.total75 = self.totalMove
        elif self.total50 and environment.currentCoverage() >= 50:
            self.total50 = self.totalMove

    def getExperimenterResult(self):
        return [self.total100, self.total90, self.total75, self.total50]
