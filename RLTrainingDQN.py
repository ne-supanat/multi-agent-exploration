# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# import numpy as np
# import os
# import copy

# from agent import Agent
# from environment import Environment
# from RLEnv import GridWorldEnv

# from constants.layoutType import LayoutType
# from constants.moveType import MoveType

# from brain.brainWandering import BrainWandering


# # Modification of Deep Q-learning by pytorch from
# # https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html

# # Modifications:
# #   - Using custom environments


# class DQN(nn.Module):
#     def __init__(self, input_dim, output_dim):
#         super(DQN, self).__init__()
#         self.fc1 = nn.Linear(input_dim, 128)
#         self.fc2 = nn.Linear(128, 128)
#         self.fc3 = nn.Linear(128, output_dim)

#     def forward(self, x):
#         x = F.relu(self.fc1(x))
#         x = F.relu(self.fc2(x))
#         return self.fc3(x)


# from collections import deque
# import random


# class ReplayMemory:
#     def __init__(self, capacity=10000):
#         self.buffer = deque(maxlen=capacity)

#     def push(self, state, action, reward, next_state, done):
#         self.buffer.append((state, action, reward, next_state, done))

#     def sample(self, batch_size):
#         batch = random.sample(self.buffer, batch_size)
#         state, action, reward, next_state, done = map(np.array, zip(*batch))
#         return state, action, reward, next_state, done

#     def __len__(self):
#         return len(self.buffer)


# def preprocess_observation(obs):
#     position = obs["position"]
#     vision = obs["vision"].flatten()
#     localmap = obs["local_map"].flatten()
#     return np.concatenate((position, vision, localmap))


# def train(
#     env: GridWorldEnv,
#     policy_net: DQN,
#     num_episodes=1000,
#     canTerminated=True,
# ):
#     # if GPU is to be used
#     device = torch.device(
#         "cuda"
#         if torch.cuda.is_available()
#         else "mps" if torch.backends.mps.is_available() else "cpu"
#     )

#     # BATCH_SIZE is the number of transitions sampled from the replay buffer
#     # GAMMA is the discount factor as mentioned in the previous section
#     # EPS_START is the starting value of epsilon
#     # EPS_END is the final value of epsilon
#     # EPS_DECAY controls the rate of exponential decay of epsilon, higher means a slower decay
#     # TARGET_UPDATE_RATE is the update rate of the target network
#     # LR is the learning rate of the ``AdamW`` optimizer
#     BATCH_SIZE = 128
#     GAMMA = 0.99
#     EPS_START = 0.9
#     EPS_END = 0.05
#     EPS_DECAY = 0.995
#     TARGET_UPDATE_RATE = 0.005
#     LR = 1e-4

#     n_actions = [type.value for type in MoveType]
#     size_actions = len(n_actions)
#     state_dim = preprocess_observation(env.reset()).shape[0]

#     target_net = DQN(state_dim, size_actions).to(device)
#     target_net.load_state_dict(policy_net.state_dict())

#     optimizer = torch.optim.Adam(policy_net.parameters(), lr=LR, amsgrad=True)
#     buffer = ReplayMemory(10000)

#     # Point to terminate episode
#     # terminatePoint = env.environment.gridMap.size * 2
#     terminatePoint = 100000

#     for episode in range(num_episodes):
#         obs = env.reset()
#         state = preprocess_observation(obs)
#         total_reward = 0

#         count = 0
#         terminated = False
#         done = False

#         while not done and not terminated:
#             # ε-greedy action selection
#             if np.random.rand() < EPS_START:
#                 action = np.random.choice(n_actions)
#             else:
#                 with torch.no_grad():
#                     state_tensor = torch.FloatTensor(state).unsqueeze(0).to(device)
#                     q_values = policy_net(state_tensor)
#                     action = q_values.argmax().item()

#             # Take action
#             next_obs, reward, done, _ = env.step(action)
#             next_state = preprocess_observation(next_obs)

#             buffer.push(state, action, reward, next_state, done)
#             state = next_state
#             total_reward += reward

#             if canTerminated:
#                 count += 1
#                 if count >= terminatePoint:
#                     terminated = True

#             # env.render()

#             # Training step
#             if len(buffer) >= BATCH_SIZE:
#                 states, actions, rewards, next_states, dones = buffer.sample(BATCH_SIZE)

#                 states = torch.FloatTensor(states).to(device)
#                 actions = torch.LongTensor(actions).unsqueeze(1).to(device)
#                 rewards = torch.FloatTensor(rewards).unsqueeze(1).to(device)
#                 next_states = torch.FloatTensor(next_states).to(device)
#                 dones = torch.FloatTensor(dones).unsqueeze(1).to(device)

#                 q_values = policy_net(states).gather(1, actions)
#                 next_q_values = target_net(next_states).max(1)[0].unsqueeze(1)
#                 target_q = rewards + GAMMA * next_q_values * (1 - dones)

#                 loss = F.mse_loss(q_values, target_q)

#                 optimizer.zero_grad()
#                 loss.backward()
#                 optimizer.step()

#         # Update ε
#         EPS_START = max(EPS_END, EPS_START * EPS_DECAY)

#         # Update target network
#         if episode % TARGET_UPDATE_RATE == 0:
#             target_net.load_state_dict(policy_net.state_dict())

#         torch.save(policy_net.state_dict(), "cw/rlModel/dqn_model.pt")
#         print(
#             f"Episode {episode+1}, Total Reward: {total_reward}, Epsilon: {EPS_START:.3f}, Move: {count}"
#         )

#         f = open("cw/rlModel/dqn_log.txt", "a")
#         f.write(
#             f"Episode {episode+1}, Total Reward: {total_reward}, Epsilon: {EPS_START:.3f}, Move: {count}\n"
#         )
#         f.close()

#     print("Complete")


# if __name__ == "__main__":
#     # fixing problem: OMP: Error #15: Initializing libomp.dylib, but found libiomp5.dylib already initialized.
#     # https://stackoverflow.com/questions/53014306/error-15-initializing-libiomp5-dylib-but-found-libiomp5-dylib-already-initial
#     os.environ["KMP_DUPLICATE_LIB_OK"] = "True"

#     # trainingLayout = [
#     #     LayoutType.RL_PLAIN_SSM,
#     #     LayoutType.RL_PLAIN_SM,
#     #     LayoutType.RL_PLAIN,
#     #     LayoutType.RL_OBSTACLES,
#     #     LayoutType.RL_MAZE,
#     # ]

#     # policy: DQN

#     # for layout in trainingLayout:
#     #     # Define custom environment
#     #     environment = Environment(layout)
#     #     agent = Agent("A0", environment.cellSize)
#     #     # friend = Agent("A1", environment.cellSize)
#     #     # friend.setBrain(BrainWandering(friend))

#     #     env = GridWorldEnv(
#     #         environment=environment,
#     #         agent=agent,
#     #         agents=[],
#     #     )

#     #     state_dim = preprocess_observation(env.reset()).shape[0]
#     #     policy = DQN(state_dim, len([type.value for type in MoveType]))
#     #     policy.load_state_dict(torch.load("cw/rlModel/dqn_model.pt", weights_only=True))

#     #     # Training process
#     #     train(env, policy)

#     baseEnvironment = Environment(None)

#     policy: DQN

#     for size in range(10, 15 + 1):
#         # Define custom environment

#         baseEnvironment.gridSize = (size, size)
#         baseEnvironment.gridMap = np.full((size, size), 2, dtype=int)
#         baseEnvironment.createBoundary()

#         environment = copy.deepcopy(baseEnvironment)
#         agent = Agent("A0", environment.cellSize)
#         # friend = Agent("A1", environment.cellSize)
#         # friend.setBrain(BrainWandering(friend))

#         env = GridWorldEnv(
#             environment=environment,
#             agent=agent,
#             agents=[],
#         )

#         state_dim = preprocess_observation(env.reset()).shape[0]
#         policy = DQN(state_dim, len([type.value for type in MoveType]))
#         if size != 10:
#             policy.load_state_dict(
#                 torch.load("cw/rlModel/dqn_model.pt", weights_only=True)
#             )

#         # Training process
#         train(env, policy)
