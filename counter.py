# This file is a modification of university of nottingham COMP4105 24-25 module's material


class Counter:
    def __init__(self):
        self.exploredCell = 0

    def explored(self, canvas):
        self.exploredCell += 1
        canvas.delete("exploredCellCount")
        canvas.create_text(
            10,
            10,
            anchor="w",
            text="Explored: " + str(self.exploredCell),
            tags="exploredCellCount",
        )

    def getExploredCell(self):
        return self.exploredCell
