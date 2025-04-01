import sqlite3
import random
import time
import math
import pygame

# Constants
DETECTION_RANGE = 500
BOT_SPEED = 0.75  # Further lowered speed for smoother and slower movement
CHANGE_DIRECTION_INTERVAL = 2  # Seconds before changing direction
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
NUM_BOTS = 5

# Load bot images
pygame.init()
bot_images = {
    "front": pygame.image.load("graphic/Ghost_Front.jpg"),
    "back": pygame.image.load("graphic/Ghost_Back.jpg"),
    "left": pygame.image.load("graphic/Ghost_Left.jpg"),
    "right": pygame.image.load("graphic/Ghost_Right.jpg")
}

def get_players():
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("SELECT player_id, position_x, position_y FROM players")
    players = cursor.fetchall()
    conn.close()
    return players

def get_bots():
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("SELECT bot_id, position_x, position_y, direction_x, direction_y, last_direction_time FROM bots")
    bots = cursor.fetchall()
    conn.close()
    return bots

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def update_bots():
    players = get_players()
    bots = get_bots()
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    current_time = time.time()

    for bot in bots:
        bot_id, bot_x, bot_y, dir_x, dir_y, last_dir_time = bot
        closest_player = None
        min_distance = float('inf')

        for player in players:
            _, player_x, player_y = player
            dist = distance(bot_x, bot_y, player_x, player_y)
            if dist < min_distance:
                min_distance = dist
                closest_player = (player_x, player_y)

        if closest_player and min_distance < DETECTION_RANGE:
            player_x, player_y = closest_player
            dx, dy = player_x - bot_x, player_y - bot_y
            length = math.sqrt(dx ** 2 + dy ** 2)
            if length != 0:
                dx, dy = (dx / length) * BOT_SPEED, (dy / length) * BOT_SPEED
            new_x, new_y = bot_x + dx, bot_y + dy
        else:
            if current_time - last_dir_time > CHANGE_DIRECTION_INTERVAL:
                dir_x, dir_y = random.choice([-1, 1]) * BOT_SPEED, random.choice([-1, 1]) * BOT_SPEED
                last_dir_time = current_time
            new_x, new_y = bot_x + dir_x, bot_y + dir_y

        new_x = max(10, min(new_x, SCREEN_WIDTH - 10))
        new_y = max(10, min(new_y, SCREEN_HEIGHT - 10))

        cursor.execute("UPDATE bots SET position_x=?, position_y=?, direction_x=?, direction_y=?, last_direction_time=? WHERE bot_id= ?",
                       (new_x, new_y, dir_x, dir_y, last_dir_time, bot_id))

    conn.commit()
    conn.close()

def draw_bots(screen, bots):
    for _, x, y, dir_x, dir_y, _ in bots:
        if dir_y < 0:
            bot_img = bot_images["front"]
        elif dir_y > 0:
            bot_img = bot_images["back"]
        elif dir_x < 0:
            bot_img = bot_images["left"]
        else:
            bot_img = bot_images["right"]
        screen.blit(bot_img, (int(x) - bot_img.get_width() // 2, int(y) - bot_img.get_height() // 2))

def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill((0, 0, 0))
        update_bots()
        bots = get_bots()
        draw_bots(screen, bots)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        clock.tick(60)

    pygame.quit()

game_loop()
