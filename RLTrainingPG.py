import numpy as np
import torch
import torch.nn as nn
from torch.distributions import Categorical
import torch.optim as optim
import os
import copy


from agent import Agent
from environment import Environment
from RLEnv import GridWorldEnv

from constants.layoutType import LayoutType

from brain.brainWandering import BrainWandering

# Modification of Policy gradient implementation by geeks for geeks from
# https://www.geeksforgeeks.org/reinforcement-learning-using-pytorch/

# Modifications:
#   - Using custom environments
#   - Not using optimizer because it cause training to crash without errors


class PolicyNetwork(nn.Module):
    def __init__(self, input_dim):
        super(PolicyNetwork, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 5),
            nn.Softmax(dim=-1),
        )

    def forward(self, x):
        return self.fc(x)


def preprocess_observation(obs):
    position = obs["position"]
    vision = obs["vision"].flatten()
    localmap = obs["local_map"].flatten()
    return np.concatenate((position, vision, localmap))


def compute_discounted_rewards(rewards, gamma=0.99):
    discounted_rewards = []
    R = 0
    for r in reversed(rewards):
        R = r + gamma * R
        discounted_rewards.insert(0, R)
    discounted_rewards = torch.tensor(discounted_rewards)
    discounted_rewards = (discounted_rewards - discounted_rewards.mean()) / (
        discounted_rewards.std() + 1e-5
    )
    return discounted_rewards


def train(
    env: GridWorldEnv,
    policy: PolicyNetwork,
    optimizer,
    num_episodes=1000,
    canTerminated=True,
):

    # terminatePoint = env.environment.gridMap.size * 2
    terminatePoint = 100000

    for episode in range(num_episodes):
        obs = env.reset()
        state = preprocess_observation(obs)
        log_probs = []
        rewards = []

        count = 0
        terminated = False
        done = False

        while not done and not terminated:
            state = torch.FloatTensor(state).unsqueeze(0)
            probs = policy(state)
            m = Categorical(probs)
            action = m.sample()
            state, reward, done, _ = env.step(action)
            state = preprocess_observation(state)
            log_probs.append(m.log_prob(action))
            rewards.append(reward)
            # Inside the train function, after an episode ends:

            if canTerminated:
                count += 1
                if count >= terminatePoint:
                    terminated = True

            # env.render()

            if done:
                discounted_rewards = compute_discounted_rewards(rewards)
                policy_loss = []
                for log_prob, Gt in zip(log_probs, discounted_rewards):
                    policy_loss.append(-log_prob * Gt)
                optimizer.zero_grad()
                policy_loss = torch.cat(policy_loss).sum()
                # print(torch.isnan(policy_loss), torch.isinf(policy_loss))
                # print(policy_loss.item())
                policy_loss.backward()
                optimizer.step()

        torch.save(policy.state_dict(), "cw/rlModel/pg_model.pt")
        print(f"Episode {episode+1}, Total Reward: {sum(rewards)}")
        f = open("cw/rlModel/pg_log.txt", "a")
        f.write(f"Episode {episode+1}, Total Reward: {sum(rewards)}\n")
        f.close()

    print("Complete")


if __name__ == "__main__":
    # fixing problem: OMP: Error #15: Initializing libomp.dylib, but found libiomp5.dylib already initialized.
    # https://stackoverflow.com/questions/53014306/error-15-initializing-libiomp5-dylib-but-found-libiomp5-dylib-already-initial
    os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

    # trainingLayout = [LayoutType.RL_PLAIN, LayoutType.RL_OBSTACLES, LayoutType.RL_MAZE]

    # policy: PolicyNetwork

    # for layout in trainingLayout:
    #     # Define custom environment
    #     environment = Environment(layout)
    #     agent = Agent("A0", environment.cellSize)
    #     # friend = Agent("A1", environment.cellSize)
    #     # friend.setBrain(BrainWandering(friend))

    #     env = GridWorldEnv(
    #         environment=environment,
    #         agent=agent,
    #         agents=[],
    #     )

    #     state_dim = preprocess_observation(env.reset()).shape[0]
    #     policy = PolicyNetwork(state_dim)
    #     optimizer = optim.Adam(policy.parameters(), lr=1e-2)
    #     policy.load_state_dict(torch.load("cw/rlModel/pg_model.pt", weights_only=True))
    #     # Training process
    #     train(env, policy, optimizer)

    baseEnvironment = Environment(None)

    policy: PolicyNetwork

    for size in range(5, 15 + 1):
        # Define custom environment

        baseEnvironment.gridSize = (size, size)
        baseEnvironment.gridMap = np.full((size, size), 2, dtype=int)
        baseEnvironment.createBoundary()

        environment = copy.deepcopy(baseEnvironment)
        agent = Agent("A0", environment.cellSize)
        # friend = Agent("A1", environment.cellSize)
        # friend.setBrain(BrainWandering(friend))

        env = GridWorldEnv(
            environment=environment,
            agent=agent,
            agents=[],
        )

        state_dim = preprocess_observation(env.reset()).shape[0]
        policy = PolicyNetwork(state_dim)
        optimizer = optim.Adam(policy.parameters(), lr=1e-2)
        if size != 5:
            policy.load_state_dict(
                torch.load("cw/rlModel/pg_model.pt", weights_only=True)
            )

        # Training process
        train(env, policy, optimizer)
