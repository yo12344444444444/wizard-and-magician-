import pygame
import sys
import socket
import json
import sqlite3
import random
import time
import math
from genericFunction import MathUtils

# קונפיגורציות
tolernsStoneSword = 10
HOST = '127.0.0.1'
PORT = 8821
DEFAULT_BUFFER_SIZE = 1024
rect_width, rect_height = 48, 93
frames_per_second = 30
window_height = 800
window_width = 1000
DETECTION_RANGE = 500
BOT_SPEED = 0.75
PLAYER_SPEED = 5
CHANGE_DIRECTION_INTERVAL = 2
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
NUM_BOTS = 5

# צבעים
WHITE = (255, 255, 255)
blue = (0, 0, 0)

# אתחול pygame
pygame.init()

# יצירת חלון
display = pygame.display.set_mode((window_width, window_height))
clock = pygame.time.Clock()
display.fill(WHITE)

# טעינת תמונות
bot_images = {
    "front": pygame.image.load("graphic/Ghost_Front.jpg"),
    "back": pygame.image.load("graphic/Ghost_Back.jpg"),
    "left": pygame.image.load("graphic/Ghost_Left.jpg"),
    "right": pygame.image.load("graphic/Ghost_Front.jpg")
}
player_image = pygame.image.load("graphic/Blue_flower.jpg")

if player_image is None:
    print("Error loading player image!")

# בקשת ערך מטבע התחלתי מהשחקן
while True:
    try:
        initial_coin = int(input("Enter your starting coin value (0-1023): "))
        if 0 <= initial_coin <= 1023:
            break
        print("Invalid input! Please enter a number between 0 and 1023.")
    except ValueError:
        print("Invalid input! Please enter a valid number.")

# נתוני שחקן
players_pos = {"a": [222, 2]}
players_coins = [0, initial_coin]

# פונקציות סוקט UDP
def build_array_of_packets(arr_obj):
    packet = f'{1:01b}' if arr_obj[0] else f'{0:01b}'
    packet += f'{ord(arr_obj[1]):07b}'.zfill(7)
    packet += f'{arr_obj[2]:011b}'.zfill(11)
    packet += f'{arr_obj[3]:011b}'.zfill(11)
    packet += f'{arr_obj[4]:010b}'.zfill(10)
    return packet

def response_to_bytes(array_for_client):
    combined_bit_string = ''.join(array_for_client)
    number = int(combined_bit_string, 2)
    byte_value = number.to_bytes((len(combined_bit_string) + 7) // 8, 'big')
    return byte_value

def parse_binary_response(binary_data):
    bit_string = ''.join(f"{byte:08b}" for byte in binary_data)
    objects = []
    for i in range(0, len(bit_string), 40):
        packet = bit_string[i:i + 40]
        if len(packet) < 40:
            continue
        rotation = int(packet[0], 2)
        object_id = chr(int(packet[1:8], 2))
        x_coord = int(packet[8:19], 2)
        y_coord = int(packet[19:30], 2)
        objects.append((bool(rotation), object_id, x_coord, y_coord))
    return objects

def get_data():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    retries = 3
    coin_value_a = players_coins[1]
    response_a = build_array_of_packets((False, "a", players_pos["a"][0], players_pos["a"][1], coin_value_a))
    response_in_bytes = response_to_bytes([response_a])

    for attempt in range(retries):
        try:
            client_socket.sendto(response_in_bytes, (HOST, PORT))
            response, _ = client_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            decoded_objects = parse_binary_response(response)
            return decoded_objects
        except ConnectionResetError as e:
            print(f"Connection reset on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                print("Retrying...")
            else:
                print("Max retries reached. Returning empty list.")
                return []
        finally:
            client_socket.close()

# פונקציות pygame ואובייקטים
def put(id):
    with open("Objects.json", "r") as f:
        y = json.load(f)
    return y["On map objects"][id]['file']

class ObjectPlacer:
    def __init__(self, pos, id):
        self.pos = pos
        self.img = pygame.image.load("graphic/" + put(id))
        display.blit(self.img, pos)

# פונקציות מסד נתונים SQLite
def get_players():
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("SELECT player_id, position_x, position_y FROM players")
    players = cursor.fetchall()
    conn.close()
    return players

def update_player_position(player_id, x, y):
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET position_x=?, position_y=? WHERE player_id=?", (x, y, player_id))
    conn.commit()
    conn.close()

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

        cursor.execute(
            "UPDATE bots SET position_x=?, position_y=?, direction_x=?, direction_y=?, last_direction_time=? WHERE bot_id= ?",
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

def draw_players(screen, players):
    for _, x, y in players:
        screen.blit(player_image, (int(x), int(y)))

# לולאת משחק ראשית
def game_loop():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(frames_per_second)
        screen.fill(WHITE)

        game_objects = get_data()
        for obj_data in game_objects:
            ObjectPlacer((obj_data[2], obj_data[3]), obj_data[1])

        update_bots()
        bots = get_bots()
        draw_bots(screen, bots)

        players = get_players()
        if not players:
            print("No players found in the database!")
            continue

        draw_players(screen, players)

        a = False # הגדרת a בתחילת כל איטרציה

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                arr = MathUtils.getObjects()
                result = next((sub_arr for sub_arr in arr if sub_arr[4] == 'b'), None)
                print(result)
                if 173 + 93 + tolernsStoneSword > y > 173 - tolernsStoneSword and 377 + 48 + tolernsStoneSword > x > 377 - tolernsStoneSword:
                    a = True

        if a:
            pygame.draw.rect(screen, blue, (x, y, rect_width, rect_height))

        # עדכון מיקום השחקן
        player_id = players[0][0]
        keys = pygame.key.get_pressed()
        player_x, player_y = players[0][1], players[0][2]

        if keys[pygame.K_w]:
            player_y = max(0, player_y - PLAYER_SPEED)
        if keys[pygame.K_s]:
            player_y = min(SCREEN_HEIGHT, player_y + PLAYER_SPEED)
        if keys[pygame.K_a]:
            player_x = max(0, player_x - PLAYER_SPEED)
        if keys[pygame.K_d]:
            player_x = min(SCREEN_WIDTH, player_x + PLAYER_SPEED)

        update_player_position(player_id, player_x, player_y)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

game_loop()