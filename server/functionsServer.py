import random
import sqlite3
from math import hypot

DATABASE = ('../DATABASE_GAME.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def choose_direction(last_direction, dx, dy):
    directions = [1, 2, 3, 4, 5]  # 1=up, 2=right, 3=down, 4=left, 5=attack
    weights = {d: 0 for d in directions}

    # 20% תקיפה
    weights[5] = 20

    # 20% לכיוון האחרון
    if last_direction in directions:
        weights[last_direction] += 20

    # חישוב הפוך למרחק – ככל שקרוב יותר, הסיכוי גבוה יותר
    dx_weight = 1 / (abs(dx) + 1)
    dy_weight = 1 / (abs(dy) + 1)
    total = dx_weight + dy_weight

    if total > 0:
        dx_part = dx_weight / total
        dy_part = dy_weight / total

        # חלוקת 60% בין צירי X ו-Y
        if dx > 0:
            weights[4] += int(60 * dx_part)  # שמאלה
        elif dx < 0:
            weights[2] += int(60 * dx_part)  # ימינה

        if dy > 0:
            weights[1] += int(60 * dy_part)  # למעלה
        elif dy < 0:
            weights[3] += int(60 * dy_part)  # למטה

    # בחירה לפי משקל
    roll = random.randint(1, 100)
    cumulative = 0
    for direction in directions:
        cumulative += weights[direction]
        if roll <= cumulative:
            return direction

def update_specific_bot(action,bot_id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # שלב 1: קח את הבוט הספציפי
    cursor.execute("SELECT * FROM bots WHERE bot_id = ?", (bot_id,))
    bot = cursor.fetchone()

    if bot:  # ודא שהבוט קיים
        if action in [1, 2, 3, 4]:
            x, y = bot['position_x'], bot['position_y']
            if action == 1:
                y += 3  # down
            elif action == 2:
                x += 3  # right
            elif action == 3:
                y -= 3  # up
            elif action == 4:
                x -= 3  # left
            cursor.execute("UPDATE bots SET position_x = ?, position_y = ? WHERE bot_id = ?", (x, y, bot_id))
            conn.commit()

        elif action == 5:
            # שלב 2: חפש שחקנים במרחק של עד 50 פיקסלים מהבוט הספציפי
            cursor.execute("SELECT * FROM players WHERE status = 'active'")
            players = cursor.fetchall()

            bot_x, bot_y = bot['position_x'], bot['position_y']
            for player in players:
                player_id = player['player_id']
                player_x, player_y = player['position_x'], player['position_y']

                distance = hypot(bot_x - player_x, bot_y - player_y)
                if distance <= 50:
                    new_health = max(0, player['health'] - 10)
                    cursor.execute("UPDATE players SET health = ? WHERE player_id = ?", (new_health, player_id))
                    print(f"Bot {bot_id} attacked Player {player_id}, new health: {new_health}")
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

def calculate_dx_dy_from_db(bot_id, player_id, db_path="../DATABASE_GAME.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # קבל את מיקום הבוט
    cursor.execute("SELECT position_x, position_y FROM bots WHERE bot_id = ?", (bot_id,))
    bot_result = cursor.fetchone()

    # קבל את מיקום השחקן
    cursor.execute("SELECT position_x, position_y FROM players WHERE player_id = ?", (player_id,))
    player_result = cursor.fetchone()

    conn.close()

    if bot_result and player_result:
        bot_x, bot_y = bot_result
        player_x, player_y = player_result

        dx = player_x - bot_x
        dy = player_y - bot_y

        return dx, dy
    else:
        return None, None  # אם אחד מהם לא נמצא

def get_all_bot_ids():
    conn = sqlite3.connect("../DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("SELECT bot_id FROM bots")
    bot_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return bot_ids

def get_closest_player_id_to_bot(bot_id):
    conn = sqlite3.connect("../DATABASE_GAME.db")
    cursor = conn.cursor()
    # מיקום הבוט
    cursor.execute("SELECT position_x, position_y FROM bots WHERE bot_id = ?", (bot_id,))
    bot_result = cursor.fetchone()
    if not bot_result:
        conn.close()
        return None
    bot_x, bot_y = bot_result
    # כל השחקנים הפעילים
    cursor.execute("SELECT player_id, position_x, position_y FROM players WHERE status = 'active'")
    players = cursor.fetchall()
    min_dist = float('inf')
    closest_player_id = None
    for player_id, player_x, player_y in players:
        dx = bot_x - player_x
        dy = bot_y - player_y
        dist = (dx**2 + dy**2)**0.5
        if dist < min_dist:
            min_dist = dist
            closest_player_id = player_id
    conn.close()
    return closest_player_id

print(get_last_bot_position(5))
