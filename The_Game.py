# PONG pygame
import os
import random
import time
import pygame, sys
from pygame.locals import *
import Network

global folder_name
global delta_time
j = 0
for i in range(0, 1001):
    if str(i).__contains__("0"):
        j += 1
print(j)
start_time = time.time()
# inputs will be score and op score, pos of ball x, pos of ball y, pos of op(x, y), pos of self(x,y)
# outputs will be move left or right
bot_1 = Network.Network([6, 8, 4], .005, 1)
bot_2 = Network.Network([6, 8, 4], .005, 2)
save_net = False
startup = input("Would you like load or save the networks?\n"
                "   (Type 'n' to run without saving or\n"
                "    loading, 'load' to load,\n"
                "    'save' to save,\n"
                "    or 'load save' to load and save')\n: ")
if startup == "load":
    folder_name = input("What is the name of the folder the weights are in?\n: ")
    bot_1.load_weights(folder_name)
    bot_2.load_weights(folder_name)
if startup == "save":
    folder_name = input("What do you want to name the folder of these networks?\n: ")
    bot_1.save_folder_name(folder_name)
    bot_2.save_folder_name(folder_name)
    save_net = True

if startup == "load save":
    folder_name = input("What is the name of the folder the weights are in?\n: ")
    bot_1.load_weights(folder_name)
    bot_2.load_weights(folder_name)
    save_net = True
pygame.init()
fps = pygame.time.Clock()

# colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# globals
WIDTH = 600
HEIGHT = 400
BALL_RADIUS = 20
PAD_WIDTH = 8
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH // 2
HALF_PAD_HEIGHT = PAD_HEIGHT // 2
ball_pos = [0, 0]
ball_vel = [0, 0]
paddle1_vel = 0
paddle2_vel = 0
l_score = 0
r_score = 0

# canvas declaration
window = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
try:
    pygame.display.set_caption(folder_name)
except NameError:
    pygame.display.set_caption("Hello World")


# helper function that spawns a ball, returns a position vector and a velocity vector
# if right is True, spawn to the right, else spawn to the left
def ball_init(right):
    global ball_pos, ball_vel  # these are vectors stored as lists
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    horz = random.randrange(2, 4)
    vert = random.randrange(-3, 3)

    if right == False:
        horz = - horz

    ball_vel = [horz, -vert]


# define event handlers
def init():
    global paddle1_pos, paddle2_pos, paddle1_vel, paddle2_vel, l_score, r_score  # these are floats
    global score1, score2  # these are ints
    paddle1_pos = [HALF_PAD_WIDTH - 1, HEIGHT // 2]
    paddle2_pos = [WIDTH + 1 - HALF_PAD_WIDTH, HEIGHT // 2]
    l_score = 0
    r_score = 0
    if random.randrange(0, 2) == 0:
        ball_init(True)
    else:
        ball_init(False)


# draw function of canvas
def draw(canvas):
    global paddle1_pos, paddle2_pos, ball_pos, ball_vel, l_score, r_score

    canvas.fill(BLACK)
    pygame.draw.line(canvas, WHITE, [WIDTH // 2, 0], [WIDTH // 2, HEIGHT], 1)
    pygame.draw.line(canvas, WHITE, [PAD_WIDTH, 0], [PAD_WIDTH, HEIGHT], 1)
    pygame.draw.line(canvas, WHITE, [WIDTH - PAD_WIDTH, 0], [WIDTH - PAD_WIDTH, HEIGHT], 1)
    pygame.draw.circle(canvas, WHITE, [WIDTH // 2, HEIGHT // 2], 70, 1)

    # update paddle's vertical position, keep paddle on the screen
    if paddle1_pos[1] > HALF_PAD_HEIGHT and paddle1_pos[1] < HEIGHT - HALF_PAD_HEIGHT:
        paddle1_pos[1] += paddle1_vel
    elif paddle1_pos[1] == HALF_PAD_HEIGHT and paddle1_vel > 0:
        paddle1_pos[1] += paddle1_vel
    elif paddle1_pos[1] == HEIGHT - HALF_PAD_HEIGHT and paddle1_vel < 0:
        paddle1_pos[1] += paddle1_vel

    if paddle2_pos[1] > HALF_PAD_HEIGHT and paddle2_pos[1] < HEIGHT - HALF_PAD_HEIGHT:
        paddle2_pos[1] += paddle2_vel
    elif paddle2_pos[1] == HALF_PAD_HEIGHT and paddle2_vel > 0:
        paddle2_pos[1] += paddle2_vel
    elif paddle2_pos[1] == HEIGHT - HALF_PAD_HEIGHT and paddle2_vel < 0:
        paddle2_pos[1] += paddle2_vel

    # update ball
    ball_pos[0] += int(ball_vel[0])
    ball_pos[1] += int(ball_vel[1])

    # draw paddles and ball
    pygame.draw.circle(canvas, RED, ball_pos, 20, 0)
    pygame.draw.polygon(canvas, GREEN, [[paddle1_pos[0] - HALF_PAD_WIDTH, paddle1_pos[1] - HALF_PAD_HEIGHT],
                                        [paddle1_pos[0] - HALF_PAD_WIDTH, paddle1_pos[1] + HALF_PAD_HEIGHT],
                                        [paddle1_pos[0] + HALF_PAD_WIDTH, paddle1_pos[1] + HALF_PAD_HEIGHT],
                                        [paddle1_pos[0] + HALF_PAD_WIDTH, paddle1_pos[1] - HALF_PAD_HEIGHT]], 0)
    pygame.draw.polygon(canvas, GREEN, [[paddle2_pos[0] - HALF_PAD_WIDTH, paddle2_pos[1] - HALF_PAD_HEIGHT],
                                        [paddle2_pos[0] - HALF_PAD_WIDTH, paddle2_pos[1] + HALF_PAD_HEIGHT],
                                        [paddle2_pos[0] + HALF_PAD_WIDTH, paddle2_pos[1] + HALF_PAD_HEIGHT],
                                        [paddle2_pos[0] + HALF_PAD_WIDTH, paddle2_pos[1] - HALF_PAD_HEIGHT]], 0)

    # ball collision check on top and bottom walls
    if int(ball_pos[1]) <= BALL_RADIUS:
        ball_vel[1] = - ball_vel[1]
    if int(ball_pos[1]) >= HEIGHT + 1 - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]

    # ball collison check on gutters or paddles
    if int(ball_pos[0]) <= BALL_RADIUS + PAD_WIDTH and int(ball_pos[1]) in range(paddle1_pos[1] - HALF_PAD_HEIGHT,
                                                                                 paddle1_pos[1] + HALF_PAD_HEIGHT, 1):
        ball_vel[0] = -ball_vel[0]
        ball_vel[0] *= 1.1
        ball_vel[1] *= 1.1
    elif int(ball_pos[0]) <= BALL_RADIUS + PAD_WIDTH:
        r_score += 1
        ball_init(True)

    if int(ball_pos[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH and int(ball_pos[1]) in range(
            paddle2_pos[1] - HALF_PAD_HEIGHT, paddle2_pos[1] + HALF_PAD_HEIGHT, 1):
        ball_vel[0] = -ball_vel[0]
        ball_vel[0] *= 1.1
        ball_vel[1] *= 1.1
    elif int(ball_pos[0]) >= WIDTH + 1 - BALL_RADIUS - PAD_WIDTH:
        l_score += 1
        ball_init(False)

    # update scores
    myfont1 = pygame.font.SysFont("Comic Sans MS", 20)
    label1 = myfont1.render("Score " + str(l_score), 1, (255, 255, 0))
    canvas.blit(label1, (50, 20))

    myfont2 = pygame.font.SysFont("Comic Sans MS", 20)
    label2 = myfont2.render("Score " + str(r_score), 1, (255, 255, 0))
    canvas.blit(label2, (470, 20))


# keydown handler
def keydown(event):
    global paddle1_vel, paddle2_vel

    if event == K_UP:
        paddle1_vel = -8
    elif event == K_DOWN:
        paddle1_vel = 8
    elif event == 0:
        paddle1_vel = 0

    elif event == K_w:
        paddle2_vel = -8
    elif event == K_s:
        paddle2_vel = 8
    elif event == -1:
        paddle2_vel = 0


# keyup handler
def keyup(event):
    global paddle1_vel, paddle2_vel

    if event in (K_w, K_s):
        paddle1_vel = 0
    elif event in (K_UP, K_DOWN):
        paddle2_vel = 0


init()


def get_move(x):
    if x % 2 == 0:
        # print("bot_1")

        output = bot_1.eval([paddle1_pos[0], paddle1_pos[1], ball_pos[0], ball_pos[1], ball_vel[0], ball_vel[1]],
                            [ball_pos, ball_vel, r_score, l_score, paddle1_pos, paddle1_vel])
        if output == 0:
            return [0, K_UP]
        elif output == 1:
            return [0, K_DOWN]
        elif output == 2:
            return [1, K_UP]
        elif output == 3:
            return [1, K_DOWN]
        else:
            # print("======================\nBot_1\n===============")
            return [0, 0]

    if x % 2 != 0:
        # print("bot_2")
        output = bot_2.eval([paddle2_pos[0], paddle2_pos[1], ball_pos[0], ball_pos[1], ball_vel[0], ball_vel[1]],
                            [ball_pos, ball_vel, l_score, r_score, paddle2_pos, paddle2_vel])
        if output == 0:
            return [0, K_w]
        if output == 1:
            return [0, K_s]
        if output == 2:
            return [1, K_w]
        if output == 3:
            return [1, K_s]
        else:
            # print("======================\nBot_2\n===============")
            return [0, -1]
    # else:
    #     return [0, 0]


# game loop
x = 0
running = True
try:
    while running:

        draw(window)
        move = get_move(x)
        # print(move)
        x += 1
        # Keep x from becoming too large
        if x == 100:
            x = 0
        if move[0] == 0:
            keydown(move[1])
        if move[0] == 1:
            keyup(move[1])
        # if x%4 ==0:

        # elif event.type == QUIT:
        #     pygame.quit()
        #     sys.exit()

        pygame.display.update()
        fps.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                delta_time = str((time.time() - start_time) / 60)

except SystemExit:
    pygame.quit()
if save_net:
    info_file_name = "Networks\\" + folder_name + "\\Info"
    info_f = open(info_file_name, "a")
    text = input("Type a little info about this network\n: ")
    data = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()) + "\n" + \
           "Delta Time : " + delta_time + "min" + "\n" + \
           folder_name + "\n" + \
           "learning rate\n" + \
           "    Bot 1: " + bot_1.learning_rate + \
           "    Bot 2: " + bot_2.learning_rate + \
           "Network Structure : " + \
           "    Bot 1: " + bot_1.layers + \
           "    Bot 2: " + bot_2.layers + \
           "Comments: " + str(text) + \
           " \n\n"
    info_f.write(str(data))
    bot_1.save()
    bot_2.save()
print("\nDone!")
