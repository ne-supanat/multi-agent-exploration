import torch
import numpy as np
from scipy.ndimage import zoom

from constants.moveType import MoveType

from brain.brain import Brain
from environment import Environment
from RLTrainingDQN import DQN
from RLTrainingPG import PolicyNetwork
from constants.gridCellType import GridCellType
import os
from centralMemory import CentralMemory


# fixing problem: OMP: Error #15: Initializing libomp.dylib, but found libiomp5.dylib already initialized.
# https://stackoverflow.com/questions/53014306/error-15-initializing-libiomp5-dylib-but-found-libiomp5-dylib-already-initial
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"


class BrainRL(Brain):
    def __init__(
        self, agentp, environment: Environment, centralMemory: CentralMemory = None
    ):
        self.agent = agentp
        self.environment = environment
        self.localMap = (
            centralMemory.map
            if not centralMemory is None
            else np.full(
                environment.gridMap.shape, GridCellType.UNEXPLORED.value, dtype=int
            )
        )

    # Decide what should be the next move
    def thinkAndAct(self, vision, agents: list) -> MoveType:
        self.updateLocalMap(vision)
        availableMoves = self.checkAvailableMoves(vision, agents)

        # Resize local map to match trained layout shape (20x20)
        h, w = self.localMap.shape
        targetSize = (20, 20)
        zoom_factors = (targetSize[0] / h, targetSize[1] / w)
        resizedLocalMap = zoom(
            self.localMap, zoom_factors, order=1
        )  # order=1 = bilinear

        obs = {
            "position": self.agent.getPosition(),
            "vision": vision,
            "local_map": resizedLocalMap,
            # "agent_positions": [agent.getPosition() for agent in self.agents],
        }

        state_dim = self.preprocess_observation(obs).shape[0]

        # Load model DQN
        policy_net = DQN(
            state_dim, len([type.value for type in MoveType])
        )  # match your original dimensions
        policy_net.load_state_dict(torch.load("dqn_model.pt", weights_only=True))
        # policy_net.eval()

        # # Load model PG
        # policy_net = PolicyNetwork(state_dim)
        # policy_net.load_state_dict(torch.load("pg_model.pt", weights_only=True))
        # # policy_net.eval()

        # Convert observation to tensor (adjust shape if needed)
        obs_tensor = torch.FloatTensor(self.preprocess_observation(obs)).unsqueeze(
            0
        )  # [1, obs_dim]

        with torch.no_grad():
            print(policy_net(obs_tensor).argmax(dim=1))
            action = policy_net(obs_tensor).argmax(dim=1).item()

        return MoveType(action) if MoveType(action) in availableMoves else MoveType.STAY

    def updateLocalMap(self, vision):
        # Update partially explored cell on gridMap
        halfVisionRow, halfVisionColumn = (
            int(self.agent.vision.shape[0] // 2),  # vision shape row
            int(self.agent.vision.shape[1] // 2),  # vision shape column
        )

        topRow = self.agent.row - halfVisionRow
        bottomRow = self.agent.row + halfVisionRow + 1
        leftColumn = self.agent.column - halfVisionColumn
        rightColumn = self.agent.column + halfVisionColumn + 1

        self.localMap[topRow:bottomRow, leftColumn:rightColumn] = vision

    def gainInfoFromVision(self, vision):
        # Update local map with value from vision
        visionRows, visionColumns = vision.shape

        for visionRow in range(visionRows):
            for visionColumn in range(visionColumns):
                targetRow = self.localRow + visionRow - int(visionRows // 2)
                targetColumn = self.localColumn + visionColumn - int(visionColumns // 2)

                self.updateLocalMapValue(
                    targetRow, targetColumn, vision[visionRow][visionColumn]
                )

                # Add new fronteir
                self.updateFronteir(
                    targetRow, targetColumn, vision[visionRow][visionColumn]
                )

    def preprocess_observation(self, obs):
        position = obs["position"]
        vision = obs["vision"].flatten()
        localmap = obs["local_map"].flatten()
        return np.concatenate((position, vision, localmap))
