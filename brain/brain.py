from constants.gridCellType import GridCellType
from constants.behaviourType import BehaviourType
from constants.moveType import MoveType


# TODO: seperate brain behavior class
class Brain:

    def __init__(self, agentp):
        self.agent = agentp

    # Decide what should be the next move
    def thinkAndAct(self, vision, agents: list) -> MoveType:
        availableMoves = self.checkAvailableMoves(vision, agents)
        return self.thinkBehavior(availableMoves)

    def checkAvailableMoves(self, vision, agents: list) -> MoveType:
        # All move type are available at first step
        availableMoves = set(MoveType)

        # Prevent hit wall and other agents
        # by filter move in that direction out if there are walls or agents
        availableMoves = self.checkWalls(availableMoves, vision)
        availableMoves = self.checkAgents(availableMoves, agents)

        return availableMoves

    def checkWalls(self, availableMoves: set[MoveType], vision) -> set[MoveType]:
        if vision[0][1] == GridCellType.WALL.value:  # check top postition
            availableMoves.discard(MoveType.UP)
        if vision[2][1] == GridCellType.WALL.value:  # check bottom postition
            availableMoves.discard(MoveType.DOWN)
        if vision[1][0] == GridCellType.WALL.value:  # check left postition
            availableMoves.discard(MoveType.LEFT)
        if vision[1][2] == GridCellType.WALL.value:  # check right postition
            availableMoves.discard(MoveType.RIGHT)

        return availableMoves

    def checkAgents(self, availableMoves: set[MoveType], agents: list) -> set[MoveType]:
        for agent in agents:
            if agent.name == self.agent:
                continue

            if agent.x == self.agent.x:
                if agent.y == self.agent.y - 1:  # check top postition
                    availableMoves.discard(MoveType.UP)
                elif agent.y == self.agent.y + 1:  # check bottom postition
                    availableMoves.discard(MoveType.DOWN)
            elif agent.y == self.agent.y:
                if agent.x == self.agent.x - 1:  # check left postition
                    availableMoves.discard(MoveType.LEFT)

                elif agent.x == self.agent.x + 1:  # check right postition
                    availableMoves.discard(MoveType.RIGHT)

        return availableMoves

    # Behavior thinking: depends on behaviour type
    def thinkBehavior(self, availableMoves) -> MoveType:
        pass
