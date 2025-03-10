import numpy as np
import torch
import torch.nn as nn
from torch.distributions import Categorical

from agent import Agent
from environment import Environment
from RLEnv import GridWorldEnv

from constants.layoutType import LayoutType

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
    full_map = obs["full_map"].flatten()
    # agent_pos = obs["agent_positions"].flatten()
    return np.concatenate(
        (
            full_map,
            # agent_pos
        )
    )


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


def train(env: GridWorldEnv, policy, episodes=1000, episode_rewards=[]):
    for episode in range(episodes):
        obs = env.reset()
        state = preprocess_observation(obs)
        log_probs = []
        rewards = []
        done = False

        while not done:
            state = torch.FloatTensor(state).unsqueeze(0)
            probs = policy(state)
            m = Categorical(probs)
            action = m.sample()
            state, reward, done, _ = env.step(action)
            state = preprocess_observation(state)
            log_probs.append(m.log_prob(action))
            rewards.append(reward)
            # Inside the train function, after an episode ends:

            env.render()

            if done:
                episode_rewards.append(sum(rewards))
                discounted_rewards = compute_discounted_rewards(rewards)
                policy_loss = []
                for log_prob, Gt in zip(log_probs, discounted_rewards):
                    policy_loss.append(-log_prob * Gt)
                policy_loss = torch.cat(policy_loss).sum()
                policy_loss.backward()

                if episode % 50 == 0:
                    print(f"Episode {episode}, Total Reward: {sum(rewards)}")
                break

    torch.save(policy.state_dict(), "pg_model.pt")
    print("Complete")


if __name__ == "__main__":
    # Define custom environment
    environment = Environment(LayoutType.TEST)
    env = GridWorldEnv(
        environment=environment,
        agent=Agent("A0", environment.cellSize),
        agents=[],
    )

    state_dim = preprocess_observation(env.reset()).shape[0]
    policy = PolicyNetwork(state_dim)

    # Training process
    train(env, policy)

    # Example of using trained model
    # TODO: remove this
    # policy.load_state_dict(torch.load("pg_model.pt", weights_only=True))
    # policy.eval()
