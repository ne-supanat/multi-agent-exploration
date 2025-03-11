import numpy as np
import torch
import torch.nn as nn
from torch.distributions import Categorical
import torch.optim as optim

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
    canTerminated=False,
):

    terminatePoint = env.environment.gridMap.size * 2

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

        print(f"Episode {episode+1}, Total Reward: {sum(rewards)}")

    torch.save(policy.state_dict(), "pg_model.pt")
    print("Complete")


if __name__ == "__main__":
    trainingLayout = [LayoutType.RL_PLAIN]
    # trainingLayout = [LayoutType.RL_PLAIN, LayoutType.RL_OBSTACLES, LayoutType.RL_MAZE]

    policy: PolicyNetwork

    for layout in trainingLayout:
        # Define custom environment
        environment = Environment(layout)
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

        # Training process
        train(env, policy, optimizer)
