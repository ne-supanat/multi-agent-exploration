import heapq
import numpy as np

from constants.gridCellType import GridCellType

# https://www.geeksforgeeks.org/introduction-to-dijkstras-shortest-path-algorithm/


def dijkstraMap(grid, src, potentialDestination):
    gridShape = grid.shape
    visited = np.full(gridShape, False)
    distanceMap = np.full(gridShape, float("inf"))
    q = []

    distanceMap[src[0], src[1]] = 0
    heapq.heappush(q, (0, src))  # (distance, position)

    hasCandidate = False

    while q:
        distance, (row, column) = heapq.heappop(q)

        if visited[row, column]:
            continue
        visited[row, column] = True

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for direction in directions:
            targetRow, targetColumn = row + direction[0], column + direction[1]

            if hasCandidate:
                distanceToSrc = abs(src[0] - targetRow) + abs(src[1] - targetColumn)
                if distanceToSrc > 10:
                    return distanceMap

            # Prevent search out of boundary
            if 0 <= targetRow < gridShape[0] and 0 <= targetColumn < gridShape[1]:
                if grid[targetRow][targetColumn] == GridCellType.WALL.value:
                    continue

                if (
                    grid[targetRow][targetColumn] == GridCellType.PARTIAL_EXPLORED.value
                    and (targetRow, targetColumn) in potentialDestination
                ):
                    hasCandidate = True

                # No data in distance map yet
                if not visited[targetRow, targetColumn]:
                    newDistance = distance + 1
                    if newDistance < distanceMap[targetRow, targetColumn]:
                        distanceMap[targetRow, targetColumn] = newDistance
                        heapq.heappush(q, (newDistance, (targetRow, targetColumn)))

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
