import sqlite3
import random
import time
import math

# Range in which bots detect players (e.g., 500 pixels)
DETECTION_RANGE = 500

def get_players():
    """ Retrieves all players from the database """
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT player_id, pose_x, pose_y, health FROM players WHERE is_bot=0")
        players = cursor.fetchall()
        print("Fetched players:", players)  # Print the fetched players
    except sqlite3.Error as e:
        print(f"Error fetching players: {e}")
        players = []  # Return an empty list in case of error
    conn.close()
    return players

def get_bots():
    """ Retrieves all bots from the database """
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT bot_id, pose_x, pose_y, health FROM bots")
        bots = cursor.fetchall()
        print("Fetched bots:", bots)  # Print the fetched bots
    except sqlite3.Error as e:
        print(f"Error fetching bots: {e}")
        bots = []  # Return an empty list in case of error
    conn.close()
    return bots

def distance(x1, y1, x2, y2):
    """ Calculates the distance between two points """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def update_bots():
    """ Updates the position of bots based on players """
    players = get_players()
    bots = get_bots()

    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()

    for bot in bots:
        bot_id, bot_x, bot_y, bot_health = bot
        closest_player = None
        min_distance = float('inf')

        print(f"Processing bot {bot_id}...")  # Print the bot being processed

        # Find the closest player
        for player in players:
            player_id, player_x, player_y, player_health = player
            dist = distance(bot_x, bot_y, player_x, player_y)
            if dist < min_distance:
                min_distance = dist
                closest_player = (player_x, player_y)

        # If a player is close, the bot attacks (e.g., reduces health)
        if closest_player and min_distance < DETECTION_RANGE:
            print(f"🔴 Bot {bot_id} attacks player at {closest_player}!")
            try:
                cursor.execute("UPDATE players SET health = health - 10 WHERE pose_x=? AND pose_y=?", closest_player)
                print(f"Player at {closest_player} health updated.")
            except sqlite3.Error as e:
                print(f"Error updating player health: {e}")
            try:
                cursor.execute("UPDATE bots SET health = health - 5 WHERE bot_id=?", (bot_id,))
                print(f"Bot {bot_id} health updated.")
            except sqlite3.Error as e:
                print(f"Error updating bot health: {e}")

        # Otherwise, the bot moves randomly
        else:
            new_x = bot_x + random.randint(-50, 50)
            new_y = bot_y + random.randint(-50, 50)
            print(f"🟢 Bot {bot_id} moves to new location: ({new_x}, {new_y})")
            try:
                cursor.execute("UPDATE bots SET pose_x=?, pose_y=? WHERE bot_id=?", (new_x, new_y, bot_id))
                print(f"Bot {bot_id} position updated.")
            except sqlite3.Error as e:
                print(f"Error updating bot position: {e}")

    conn.commit()
    conn.close()

# Run in a loop (execute every 3 seconds)
while True:
    update_bots()
    time.sleep(3)