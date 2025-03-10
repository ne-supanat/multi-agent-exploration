import random
import torch
import numpy as np
import copy

from constants.moveType import MoveType

from brain.brain import Brain
from constants.layoutType import LayoutType
from environment import Environment
from RLEnv import GridWorldEnv
from RLTrainingDQN import DQN
from RLTrainingPG import PolicyNetwork
import os

# fixing problem: OMP: Error #15: Initializing libomp.dylib, but found libiomp5.dylib already initialized.
# https://stackoverflow.com/questions/53014306/error-15-initializing-libiomp5-dylib-but-found-libiomp5-dylib-already-initial
os.environ["KMP_DUPLICATE_LIB_OK"] = "True"


class BrainRL(Brain):
    # Decide what should be the next move
    def thinkAndAct(self, vision, agents: list) -> MoveType:
        availableMoves = self.checkAvailableMoves(vision, agents)

        # Load environment
        copy_obj = copy.copy(self.agent)
        environment = Environment(LayoutType.TEST)
        env = GridWorldEnv(
            environment=environment,
            agent=copy_obj,
            agents=[],
        )
        obs = env.reset()

        n_actions = [type.value for type in MoveType]
        size_actions = len(n_actions)
        state_dim = self.preprocess_observation(env.reset()).shape[0]

        # Load model DQN
        policy_net = DQN(state_dim, size_actions)  # match your original dimensions
        policy_net.load_state_dict(torch.load("dqn_model.pt"))
        policy_net.eval()

        # # Load model PG
        # policy_net = PolicyNetwork(state_dim)
        # policy_net.load_state_dict(torch.load("pg_model.pt", weights_only=True))
        # policy_net.eval()

        # Convert observation to tensor (adjust shape if needed)
        obs_tensor = torch.FloatTensor(self.preprocess_observation(obs)).unsqueeze(
            0
        )  # [1, obs_dim]

        with torch.no_grad():
            action = policy_net(obs_tensor).argmax(dim=1).item()

        return MoveType(action) if MoveType(action) in availableMoves else MoveType.STAY

    def preprocess_observation(self, obs):
        full_map = obs["full_map"].flatten()
        # agent_pos = obs["agent_positions"].flatten()
        return np.concatenate(
            (
                full_map,
                # agent_pos
            )
        )

    # Behavior thinking: depends on behaviour type
    def thinkBehavior(self, availableMoves) -> MoveType:
        pass
