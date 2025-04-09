import socket
import json
import time
import sqlite3
import math
import random

import myEmenies
from genericFunction import MathUtils

# Constants
clint = '192.168.1.79'
PORT = 8826
DEFAULT_BUFFER_SIZE = 1024
DETECTION_RANGE = 500
BOT_SPEED = 0.75
CHANGE_DIRECTION_INTERVAL = 2
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Initialize server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((clint, PORT))

def get_players():
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("SELECT player_id, position_x, position_y FROM players")
    data = cursor.fetchall()
    conn.close()
    return data

def get_bots(conn, cursor):
    cursor.execute("SELECT bot_id, position_x, position_y, last_direction_time FROM bots")
    return cursor.fetchall()

def update_bots():
    players = get_players()
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    bots = get_bots(conn, cursor)
    current_time = time.time()

    updates = []

    for bot in bots:
        bot_id, bot_x, bot_y, last_dir_time = bot
        closest_player = None
        min_dist = float("inf")

        for _, px, py in players:
            dist = math.hypot(px - bot_x, py - bot_y)
            if dist < min_dist:
                min_dist = dist
                closest_player = (px, py)

        if closest_player and min_dist < DETECTION_RANGE:
            dx, dy = closest_player[0] - bot_x, closest_player[1] - bot_y
            length = math.hypot(dx, dy)
            if length != 0:
                dx = (dx / length) * BOT_SPEED
                dy = (dy / length) * BOT_SPEED
        else:
            if current_time - last_dir_time > CHANGE_DIRECTION_INTERVAL:
                dir_x = random.choice([-1, 1]) * BOT_SPEED
                dir_y = random.choice([-1, 1]) * BOT_SPEED
                last_dir_time = current_time

        new_x = max(10, min(bot_x, SCREEN_WIDTH - 10))
        new_y = max(10, min(bot_y , SCREEN_HEIGHT - 10))

        updates.append((new_x, new_y, last_dir_time, bot_id))
        print(updates)
       # MathUtils.parse_binary_response()
    cursor.executemany(
        "UPDATE bots SET position_x=?, position_y=?, last_direction_time=? WHERE bot_id=?",
        updates
    )
    conn.commit()
    conn.close()

def handle_client(data, addr):
    try:
        player_data = MathUtils.parse_binary_response(data)
        print(player_data)
    except Exception as e:
        print("Parse error:", e)
        return

    # Load current player database
    try:
        with open("ips.json", "r") as f:
            y = json.load(f)
    except:
        y = {"players": {}}

    if "players" not in y:
        y["players"] = {}

    updated_ids = set()
    for obj in player_data:
        obj_id = obj[4]
        y["players"][obj_id] = {"pose": f"{obj[2]},{obj[3]}", "id": obj[1]}
        updated_ids.add(obj_id)

    with open("ips.json", "w") as f:
        json.dump(y, f, indent=1)

    # Filter objects within range (optimized)
  #  print(myEmenies.get_objects_near_player())
    arr_obj = []
    for obj_id, data in y["players"].items():
        x, y_pos = map(int, data["pose"].split(","))
        if abs(x - obj[2]) < 960:  # only filter by x for speed
            arr_obj.append((False, data["id"], x, y_pos, obj_id))

    if arr_obj:
        packets = [MathUtils.build_array_of_packets(o) for o in arr_obj]
        packet_bytes = MathUtils.response_to_bytes(packets)
        server_socket.sendto(packet_bytes, addr)

def allowUtalk():
    BUFFER_SIZE = 1024

    print("Server is listening...")
    r=True
    while r:
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        print(f"Received from {addr}: {data.decode()}")

        if data.decode().lower() == "hello":
            server_socket.sendto(b"1", addr)
            r = False
def main():
    print("Fast UDP Server Running")
    last_bot_update = 0

    while True:
        data, addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
        handle_client(data, addr)

        # Update bots every 1/30th of a second
        if time.time() - last_bot_update > 1 / 30:
            update_bots()
            last_bot_update = time.time()

allowUtalk()
main()
