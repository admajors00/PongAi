import numpy as np
import random
# import The_Game
import operator
import pickle
import os
import time


class Network:
    def __init__(self, layers, learning_rate, player_num):
        self.start_time = time.time()
        self.layers = layers
        self.net_list = [[]]
        self.predicted_reward = []
        self.num_inputs = layers[0]
        self.weights = [[], [], []]
        self.biases = [[], [], []]
        self.curiosity = .1
        self.learning_rate = learning_rate
        self.player_num = player_num
        self.input = []
        self.outputs = []
        self.time = 0
        self.folder_name = ""

        self.sum_error = int
        self.wins = 0
        self.losses = 0

        temp = []
        for i in range(len(self.layers) - 1):
            for j in range(self.layers[i + 1]):
                self.biases[i + 1].append(random.random())
                for k in range(self.layers[i]):
                    temp.append(random.random())
                temp = np.array(temp)
                self.weights[i + 1].append(temp)
                temp = []

    def init_network(self):
        # self.weights = np.array(self.weights)
        # print("Network #", self.player_num, "\n=============================\n")
        # for layer in self.weights:
        #     print("\n\n==============")
        #     for node in layer:
        #         print(node, "\n")
        x = 0

    def load_weights(self, folder_name):
        self.folder_name = os.path.join("Networks", folder_name, "_Net" + str(self.player_num))
        net_biases = self.folder_name + "\\Biases"
        net_weights = self.folder_name + "\\Weights"
        biases_f1 = open(net_biases, 'rb')
        weights_f1 = open(net_weights, 'rb')
        self.biases = pickle.load(biases_f1)
        self.weights = pickle.load(weights_f1)
        self.weights = np.array(self.weights)

    def save_folder_name(self, folder_name):
        u = os.path.join("Networks", folder_name, "_Net" + str(self.player_num))
        os.makedirs(u)
        self.folder_name = u

    def save(self):
        # print("folder name : ", self.folder_name)
        w_file_name = self.folder_name + "\\Weights"
        weights_f = open(w_file_name, 'wb')
        pickle._dump(self.weights, weights_f)
        weights_f.close()

        b_file_name = self.folder_name + "\\Biases"
        biases_f = open(b_file_name, 'wb')
        pickle.dump(self.biases, biases_f)
        biases_f.close()

    def eval(self, board_inputs, info):
        # this function estimates the reward
        if random.random() > .95:
            number = random.randint(0, 4)
        else:
            self.time += 1
            self.input = board_inputs
            self.curiosity += self.time * .01
            self.outputs = []

            x = 0
            inputs = []
            for k in range(len(board_inputs)):
                inputs.append([board_inputs[k]])

            for i in range(len(self.layers) - 1):
                if x >= 1:
                    inputs = np.array(self.predicted_reward)
                self.predicted_reward.clear()
                temp_out = []
                x += 1
                for j in range(self.layers[i + 1]):
                    temp_out.insert(-1,
                                    sigmoid((float(np.dot(self.weights[i + 1][j], inputs)) + self.biases[i + 1][j])))
                for l in range(len(temp_out)):
                    self.predicted_reward.append([temp_out[l]])
                self.outputs.append(temp_out.copy())
                temp_out = []
            self.outputs.insert(0, self.input.copy())
            number = (self.predicted_reward.index(max(self.predicted_reward)))
            # print(self.predicted_reward)
            # print(number)
            confidence = np.round(self.predicted_reward[number][0] * 100, 3)
            self.backward_propagate_error(info)
        # print(number)
        return number

        # except TypeError:
        #     print("Type Error\n   Returning Random Number")
        #     return random.randint(0,6)

    def backward_propagate_error(self, info):
        # for layer in self.weights:
        #     print("==============")
        #     for node in layer:
        #         print("\n")
        #         for weight in node:
        #             print(weight)
        actual_reward = np.array(self.find_rewards(info))

        # print("act : ", actual_reward, "\n outputs : ", self.outputs)
        self.sum_error = sum(actual_reward - np.array(self.predicted_reward)) ** 2
        # print("Sum Error = ", self.sum_error)
        delta_weights = [[], [], []]
        for i in reversed(range(len(self.layers))):
            errors = [[], [], []]
            if i != len(self.layers) - 1:
                for j in range(self.layers[i]):
                    error = 0.0
                    # error += self.biases[i+1][j]
                    for k in range(len(self.weights[i + 1]) - 1):
                        error += self.weights[i + 1][k][j] * delta_weights[i + 1][k]
                    errors[i].append(error)
            else:
                # print("outputs : ", self.outputs)

                for j in range(self.layers[i]):
                    error = (actual_reward[j] - self.outputs[i - 1][j])
                    errors[i].append(error)

            for j in range(self.layers[i]):
                delta_weights[i].append(errors[i][j] * sigmoid_derivative(self.outputs[i][j]))
        self.update_weights(delta_weights)

    def update_weights(self, delta_weights):
        for i in range(len(self.layers) - 1):
            # print("i : ", i)
            inputs = self.input.copy()
            if i != 0:
                inputs = self.outputs[i]
            for j in range(self.layers[i] - 6):
                # print('    j : ', j )
                for k in range(len(inputs)):
                    # print("        k : ", k)
                    self.weights[i + 1][j][k] += self.learning_rate * delta_weights[i + 1][j] * inputs[k]
                self.biases[i + 1] += self.learning_rate * delta_weights[i + 1][j]

    def find_rewards(self, info):
        # an increase in players score is +250 -250 for increase in op score
        # if the bot chooses a dir to that it cant (against a wall) -50
        # The distance in the y direction the ball is from the paddle *-100

        discount_factor = .95

        rewards = []
        reward = 0
        expected_future_rewards = []
        expected_future_reward = 0

        for i in range(0, self.layers[-1]):
            reward = 0
            evaluated = info

            ball_pos = evaluated[0]
            ball_vel = evaluated[1]
            score = evaluated[2]
            op_score = evaluated[3]
            pos = evaluated[4]
            vel = evaluated[5]
            # has_lost = evaluated[4]
            if i == 0:
                pos[1] += vel
            if i == 1:
                pos[1] -= vel
            #reward += score - op_score * 100
            reward -= abs(ball_pos[1] - pos[1]) * 500
            # add oponents predicten move here
            expected_future_rewards = []
            for k in range(0, self.layers[-1]):
                expected_future_reward = 0
                expected_future_reward = abs(ball_pos[1] + ball_vel[1] - pos[1]) * 500
                expected_future_rewards.append(expected_future_reward)
            expected_future_reward = max(expected_future_rewards)
            reward += expected_future_reward * discount_factor
            rewards.append(sigmoid(reward))
            # print(rewards)
        return rewards


def sigmoid(z):
    sig = 1.0 / (1.0 + (np.exp(-z)))
    return sig


def sigmoid_derivative(x):
    return x * (1 - x)


class Node:
    def __init__(self, weight, bias):
        self.weight = weight
        self.bias = bias

    def weight(self):
        return self.weight

    def bias(self):
        return self.bias
