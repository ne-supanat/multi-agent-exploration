# This file is a modification of university of nottingham COMP4105 24-25 module's material


class Counter:
    def __init__(self, mapSize):
        self.exploredCell = 0
        self.totalMove = 0
        self.mapSize = mapSize

    def moved(self, canvas):
        self.totalMove += 1
        canvas.delete("totalMoveCount")
        canvas.create_text(
            10,
            self.mapSize[0] + 30,
            anchor="w",
            text="Moved: " + str(self.totalMove),
            tags="totalMoveCount",
        )

    def explored(self, canvas):
        self.exploredCell += 1
        canvas.delete("exploredCellCount")
        canvas.create_text(
            10,
            self.mapSize[0] + 15,
            anchor="w",
            text="Explored: " + str(self.exploredCell),
            tags="exploredCellCount",
        )

    def getExploredCell(self):
        return self.exploredCell

    def getTotalMove(self):
        return self.totalMove
