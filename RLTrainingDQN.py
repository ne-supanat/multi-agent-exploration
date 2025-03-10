import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

from agent import Agent
from environment import Environment
from RLEnv import GridWorldEnv

from constants.layoutType import LayoutType
from constants.moveType import MoveType

# Modification of Deep Q-learning by pytorch from
# https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html

# Modifications:
#   - Using custom environments


class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, output_dim)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)


from collections import deque
import random


class ReplayMemory:
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = map(np.array, zip(*batch))
        return state, action, reward, next_state, done

    def __len__(self):
        return len(self.buffer)


def preprocess_observation(obs):
    full_map = obs["full_map"].flatten()
    # agent_pos = obs["agent_positions"].flatten()
    return np.concatenate(
        (
            full_map,
            # agent_pos
        )
    )


def train(env: GridWorldEnv, num_episodes=1000):
    # if GPU is to be used
    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available() else "cpu"
    )

    # BATCH_SIZE is the number of transitions sampled from the replay buffer
    # GAMMA is the discount factor as mentioned in the previous section
    # EPS_START is the starting value of epsilon
    # EPS_END is the final value of epsilon
    # EPS_DECAY controls the rate of exponential decay of epsilon, higher means a slower decay
    # TARGET_UPDATE_RATE is the update rate of the target network
    # LR is the learning rate of the ``AdamW`` optimizer
    BATCH_SIZE = 128
    GAMMA = 0.99
    EPS_START = 0.9
    EPS_END = 0.05
    EPS_DECAY = 0.995
    TARGET_UPDATE_RATE = 0.005
    LR = 1e-4

    n_actions = [type.value for type in MoveType]
    size_actions = len(n_actions)
    state_dim = preprocess_observation(env.reset()).shape[0]

    policy_net = DQN(state_dim, size_actions).to(device)
    target_net = DQN(state_dim, size_actions).to(device)
    target_net.load_state_dict(policy_net.state_dict())

    optimizer = torch.optim.Adam(policy_net.parameters(), lr=LR, amsgrad=True)
    buffer = ReplayMemory(10000)

    for episode in range(num_episodes):
        obs = env.reset()
        state = preprocess_observation(obs)
        total_reward = 0

        done = False
        while not done:
            # ε-greedy action selection
            if np.random.rand() < EPS_START:
                action = np.random.choice(n_actions)
            else:
                with torch.no_grad():
                    state_tensor = torch.FloatTensor(state).unsqueeze(0).to(device)
                    q_values = policy_net(state_tensor)
                    action = q_values.argmax().item()

            # Take action
            next_obs, reward, done, _ = env.step(action)
            next_state = preprocess_observation(next_obs)

            buffer.push(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward

            env.render()

            # Training step
            if len(buffer) >= BATCH_SIZE:
                states, actions, rewards, next_states, dones = buffer.sample(BATCH_SIZE)

                states = torch.FloatTensor(states).to(device)
                actions = torch.LongTensor(actions).unsqueeze(1).to(device)
                rewards = torch.FloatTensor(rewards).unsqueeze(1).to(device)
                next_states = torch.FloatTensor(next_states).to(device)
                dones = torch.FloatTensor(dones).unsqueeze(1).to(device)

                q_values = policy_net(states).gather(1, actions)
                next_q_values = target_net(next_states).max(1)[0].unsqueeze(1)
                target_q = rewards + GAMMA * next_q_values * (1 - dones)

                loss = F.mse_loss(q_values, target_q)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        # Update ε
        EPS_START = max(EPS_END, EPS_START * EPS_DECAY)

        # Update target network
        if episode % TARGET_UPDATE_RATE == 0:
            target_net.load_state_dict(policy_net.state_dict())

        print(f"Episode {episode+1}, Reward: {total_reward}, Epsilon: {EPS_START:.3f}")

    torch.save(policy_net.state_dict(), "dqn_model.pt")
    print("Complete")


if __name__ == "__main__":
    # Define custom environment
    environment = Environment(LayoutType.TEST)
    env = GridWorldEnv(
        environment=environment,
        agent=Agent("A0", environment.cellSize),
        agents=[],
    )

    # Training process
    train(env)

    # Example of using trained model
    # TODO: remove this
    # n_actions = [type.value for type in MoveType]
    # size_actions = len(n_actions)
    # state_dim = preprocess_observation(env.reset()).shape[0]

    # policy_net = DQN(state_dim, size_actions)
    # policy_net.load_state_dict(torch.load("dqn_model.pt", weights_only=True))
    # policy_net.eval()
