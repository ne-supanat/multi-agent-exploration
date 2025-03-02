import numpy as np


class CentralMap:
    def __init__(self, sizeRow, sizeColumn):
        self.map = np.zeros((sizeRow, sizeColumn))
        self.frontiers = []
        self.blackboard = {}

    def addRowAbove(self, noOfRows):
        self.map = np.vstack((np.zeros((noOfRows, self.map.shape[1])), self.map))

    def addRowBelow(self, noOfRows):
        self.map = np.vstack((self.map, np.zeros((noOfRows, self.map.shape[1]))))

    def addColumnLeft(self, noOfColumns):
        self.map = np.hstack((np.zeros((self.map.shape[0], noOfColumns)), self.map))

    def addColumnRight(self, noOfColumns):
        self.map = np.hstack((self.map, np.zeros((self.map.shape[0], noOfColumns))))

    def updateValueAt(self, column, row, value):
        self.map[row, column] = value

    def addFrontierPos(self, pos):
        self.frontiers.append(pos)

    def removeFrontierPos(self, pos):
        self.frontiers.remove(pos)
