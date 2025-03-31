import sqlite3
import random
import math
import socket

# Attack range configurations and bot speed
CLOSE_ATTACK_RANGE = 200  # Close range for bot
FAR_ATTACK_RANGE = 600  # Far range for bot
BOT_SPEED = 10  # Bot movement speed towards the player
MAX_BOTS = 100  # Maximum number of bots on the map

# Server configurations
HOST = '127.0.0.1'
PORT = 8821
DEFAULT_BUFFER_SIZE = 1024


def get_players():
    """Fetches the list of players from the database."""
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("SELECT player_id, pose_x, pose_y, health FROM players WHERE is_bot=0")
    players = cursor.fetchall()
    conn.close()
    return players


def get_bots():
    """Fetches the list of bots from the database."""
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("SELECT bot_id, pose_x, pose_y, health, attack_type FROM bots")
    bots = cursor.fetchall()
    conn.close()
    return bots


def count_bots():
    """Returns the current number of active bots in the database."""
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM bots")
    bot_count = cursor.fetchone()[0]
    conn.close()
    return bot_count


def add_missing_bots():
    """Ensures that there are always 100 bots on the map by adding missing bots."""
    current_bot_count = count_bots()
    missing_bots = MAX_BOTS - current_bot_count

    if missing_bots > 0:
        conn = sqlite3.connect("DATABASE_GAME.db")
        cursor = conn.cursor()

        for _ in range(missing_bots):
            new_x = random.randint(100, 900)  # Random x-coordinate for bot
            new_y = random.randint(100, 700)  # Random y-coordinate for bot
            health = 100
            attack_type = random.choice(["close", "far"])  # Random attack type
            cursor.execute("INSERT INTO bots (pose_x, pose_y, health, attack_type) VALUES (?, ?, ?, ?)",
                           (new_x, new_y, health, attack_type))
            print(f"Added new {attack_type} bot at ({new_x}, {new_y})")

        conn.commit()
        conn.close()


def distance(x1, y1, x2, y2):
    """Calculates the distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def move_towards(bot_x, bot_y, player_x, player_y):
    """Moves the bot towards the player's position."""
    angle = math.atan2(player_y - bot_y, player_x - bot_x)
    new_x = bot_x + BOT_SPEED * math.cos(angle)
    new_y = bot_y + BOT_SPEED * math.sin(angle)
    return int(new_x), int(new_y)


def move_randomly(bot_x, bot_y):
    """Moves the bot randomly."""
    new_x = bot_x + random.randint(-50, 50)
    new_y = bot_y + random.randint(-50, 50)
    return int(new_x), int(new_y)


def update_bots():
    """Updates the bots’ positions and health based on interactions with players."""
    players = get_players()
    bots = get_bots()

    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()

    for bot in bots:
        bot_id, bot_x, bot_y, bot_health, attack_type = bot
        closest_player = None
        min_distance = float('inf')

        # Find the closest player
        for player in players:
            player_id, player_x, player_y, player_health = player
            dist = distance(bot_x, bot_y, player_x, player_y)
            if dist < min_distance:
                min_distance = dist
                closest_player = (player_x, player_y, player_id)

        # If a player is close enough
        if closest_player:
            player_x, player_y, player_id = closest_player
            attack_range = CLOSE_ATTACK_RANGE if attack_type == "close" else FAR_ATTACK_RANGE

            if min_distance < attack_range:
                # Bot is in attack range and attacks the player
                print(f"Bot {bot_id} attacks Player {player_id}!")
                cursor.execute("UPDATE players SET health = health - 10 WHERE player_id=?", (player_id,))
            else:
                # Bot is not in range, so it moves randomly
                new_x, new_y = move_randomly(bot_x, bot_y)
                cursor.execute("UPDATE bots SET pose_x=?, pose_y=? WHERE bot_id=?", (new_x, new_y, bot_id))
        else:
            # No players close, bot moves randomly
            new_x, new_y = move_randomly(bot_x, bot_y)
            cursor.execute("UPDATE bots SET pose_x=?, pose_y=? WHERE bot_id=?", (new_x, new_y, bot_id))

        # If bot is dead (health <= 0), it is replaced with a new bot
        if bot_health <= 0:
            print(f"Bot {bot_id} died. Replacing with a new bot.")
            new_x = random.randint(100, 900)
            new_y = random.randint(100, 700)
            health = 100
            attack_type = random.choice(["close", "far"])
            cursor.execute("UPDATE bots SET pose_x=?, pose_y=?, health=?, attack_type=? WHERE bot_id=?",
                           (new_x, new_y, health, attack_type, bot_id))

    conn.commit()
    conn.close()


def build_bot_packet(bot):
    """Creates a binary packet to send bot information to clients."""
    bot_id, bot_x, bot_y, bot_health, attack_type = bot
    is_bot = 1  # Mark this as a bot
    bot_char = 'B'  # Identifier for the object
    attack_type_bin = '01' if attack_type == "close" else '10'  # Close range 01, Far range 10
    return f'{is_bot:01b}{ord(bot_char):07b}{bot_x:011b}{bot_y:011b}{attack_type_bin:02b}'


def send_bots_to_clients():
    """Listens for clients and sends bot data to them."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        data, client_address = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)

        add_missing_bots()  # Add any missing bots
        update_bots()  # Update bot states
        bots = get_bots()  # Fetch current bot data

        # Build the binary data for all bots
        bot_packets = [build_bot_packet(bot) for bot in bots]
        response_binary = ''.join(bot_packets)
        response_bytes = int(response_binary, 2).to_bytes((len(response_binary) + 7) // 8, 'big')

        # Send the binary data to the client
        server_socket.sendto(response_bytes, client_address)


# Start the server to send bot data to clients
send_bots_to_clients()
