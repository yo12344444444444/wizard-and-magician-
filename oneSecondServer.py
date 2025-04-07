import sqlite3
import random
import time
import math
import pygame
import sys
import socket
import json
from genericFunction import MathUtils

# Constants
DETECTION_RANGE = 500
BOT_SPEED = 0.75
CHANGE_DIRECTION_INTERVAL = 2
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
NUM_BOTS = 5
HOST = '127.0.0.1'
PORT = 8822
DEFAULT_BUFFER_SIZE = 1024

tolernsStoneSword = 10
x, y, rect_width, rect_height = 200, 150, 48, 93
a = False

# Initialize pygame
pygame.init()
def handle_client(packed_data, server_socket, client_addr):
    # Load existing player data from the JSON file
    try:
        with open("ips.json", "r") as f:
            y = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        y = {"players": {}}

    if "players" not in y:
        y["players"] = {}

    # Parse the incoming data
    player_data = MathUtils.parse_binary_response(packed_data)
    if not player_data:
        print(f"Invalid data from {client_addr}, ignoring...")
        return

    updated_ids = set()  # Track updated player IDs

    # Process received player data
    player_x, player_y = None, None
    for obj in player_data:
        obj_id = obj[4]
        if obj_id not in y["players"]:
            y["players"][obj_id] = {"pose": f"{obj[2]},{obj[3]}", "id": obj[1]}
        else:
            y["players"][obj_id]["pose"] = f"{obj[2]},{obj[3]}"
        updated_ids.add(obj_id)

        # Save current player's position
        player_x, player_y = obj[2], obj[3]



    # **Keep all existing players** (don't delete missing ones)

    # Save updated player data to the JSON file
    with open("ips.json", "w") as f:
        json.dump(y, f, indent=1)

    # Prepare the response for all players
    arr_obj = []
    for obj_id, data in y["players"].items():
        x, y_pos = map(int, data["pose"].split(","))
        if (obj[2]-(1920/2)<x<obj[2]+(1920/2)):
            pass
        id = data["id"]
        arr_obj.append((False,id , x, y_pos, obj_id))

    if not arr_obj:
        print("No objects found, sending empty response.")
        return

    # Build and send response packets
    response = [MathUtils.build_array_of_packets(obj) for obj in arr_obj]
    response_in_bytes = MathUtils.response_to_bytes(response)
    server_socket.sendto(response_in_bytes, client_addr)

# Load bot images
bot_images = {
    "up": pygame.image.load("graphic/Ghost_Back.png"),
    "down": pygame.image.load("graphic/Ghost_Front.png"),
    "left": pygame.image.load("graphic/Ghost_Left.png"),
    "right": pygame.image.load("graphic/Ghost_Right.png")
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
            bot_img = bot_images["up"]
        elif dir_y > 0:
            bot_img = bot_images["down"]
        elif dir_x < 0:
            bot_img = bot_images["left"]
        else:
            bot_img = bot_images["right"]
        screen.blit(bot_img, (int(x) - bot_img.get_width() // 2, int(y) - bot_img.get_height() // 2))


server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

def game_loop():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True
    players_pos = {"a": [222, 2]}
    players_coins = [0, 100]

    while running:
        packed_data, client_addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
        handle_client(packed_data, server_socket, client_addr)
        screen.fill((0, 0, 0))
        update_bots()
        bots = get_bots()
        draw_bots(screen, bots)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            players_pos["a"][1] -= 5
        if keys[pygame.K_s]:
            players_pos["a"][1] += 5
        if keys[pygame.K_a]:
            players_pos["a"][0] -= 5
        if keys[pygame.K_d]:
            players_pos["a"][0] += 5

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

game_loop()