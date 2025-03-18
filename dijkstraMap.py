import heapq
import numpy as np

from constants.gridCellType import GridCellType

# https://www.geeksforgeeks.org/introduction-to-dijkstras-shortest-path-algorithm/


def dijkstraMap(grid, src):
    gridShape = grid.shape
    visited = np.full(gridShape, False)
    distanceMap = np.full(gridShape, float("inf"))
    q = []

    distanceMap[src[0], src[1]] = 0
    heapq.heappush(q, (src, 0))

    while q:
        node = heapq.heappop(q)
        (row, column), distance = node

        visited[row, column] = True

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for direction in directions:
            targetRow, targetColumn = row + direction[0], column + direction[1]
            # Prevent search out of boundary
            if (
                targetRow >= 0
                and targetRow < gridShape[0]
                and targetColumn >= 0
                and targetColumn < gridShape[1]
            ):
                if grid[targetRow][targetColumn] == GridCellType.WALL.value:
                    continue

                if not visited[targetRow, targetColumn]:
                    newDistance = distance + 1

                    # No data in distance map yet
                    if distanceMap[targetRow, targetColumn] == 0:
                        distanceMap[targetRow, targetColumn] = newDistance
                    else:
                        if newDistance < distanceMap[targetRow, targetColumn]:
                            distanceMap[targetRow, targetColumn] = newDistance
                            heapq.heappush(q, ((targetRow, targetColumn), newDistance))

    return distanceMap


def dijkstraSearch(distanceMap, potentialDestination):
    bestDestination = None
    minDistance = float("inf")

    for dest in potentialDestination:
        destRow, destColumn = dest
        distance = distanceMap[destRow, destColumn]
        if distance < minDistance:
            minDistance = distance
            bestDestination = dest

    return bestDestination
