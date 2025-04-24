import random
import sqlite3
from math import hypot

DATABASE = ('../DATABASE_GAME.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def choose_direction(last_direction):
    directions = [1, 2, 3, 4, 5]  # Including attack = 5

    # Start with equal weight
    weights = {d: 0 for d in directions}

    if last_direction in directions:
        # Assign 20% to the last direction
        weights[last_direction] = 20

        # Distribute remaining 80% to others
        others = [d for d in directions if d != last_direction]
        for d in others:
            weights[d] = 80 // len(others)
    else:
        # If no valid last direction, distribute equally
        for d in directions:
            weights[d] = 100 // len(directions)

    # Weighted random choice
    roll = random.randint(1, 100)
    cumulative = 0
    for direction, chance in weights.items():
        cumulative += chance
        if roll <= cumulative:
            return direction


def update_bots_based_on_random_action(action):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # שלב 1: קח את כל הבוטים
    cursor.execute("SELECT * FROM bots")
    bots = cursor.fetchall()

    if action in [1, 2, 3, 4]:
        for bot in bots:
            x, y = bot['position_x'], bot['position_y']
            if action == 1:
                y += 1  # למטה
            elif action == 2:
                x += 1  # ימינה
            elif action == 3:
                y -= 1  # למעלה
            elif action == 4:
                x -= 1  # שמאלה
            cursor.execute("UPDATE bots SET position_x = ?, position_y = ? WHERE bot_id = ?", (x, y, bot['bot_id']))
        conn.commit()

    elif action == 5:
        # שלב 2: עבור כל בוט חפש שחקן במרחק של עד 50 פיקסלים
        cursor.execute("SELECT * FROM players WHERE status = 'active'")
        players = cursor.fetchall()

        for bot in bots:
            bot_x, bot_y = bot['position_x'], bot['position_y']
            for player in players:
                player_id = player['player_id']
                player_x, player_y = player['position_x'], player['position_y']

                distance = hypot(bot_x - player_x, bot_y - player_y)
                if distance <= 50:
                    new_health = max(0, player['health'] - 10)
                    cursor.execute("UPDATE players SET health = ? WHERE player_id = ?", (new_health, player_id))
                    print(f"Bot {bot['bot_id']} attacked Player {player_id}, new health: {new_health}")
        conn.commit()

    conn.close()
def get_last_bot_position(bot_id):
    conn = sqlite3.connect("../DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("SELECT last_direction FROM bots WHERE bot_id = ?", (bot_id,))
    position = cursor.fetchone()
    conn.close()

    if position:
        return position[0]  # מחזיר tuple: (position_x, position_y)
    else:
        return None

print(get_last_bot_position(5))
