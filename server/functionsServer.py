import random
import sqlite3
import time
from math import hypot
import datetime

from urllib3.filepost import choose_boundary

DATABASE = ('../DATABASE_GAME.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def choose_direction(last_direction, dx, dy):
    directions = [1, 2, 3, 4, 5]  # 1=up, 2=right, 3=down, 4=left, 5=attack
    weights = {d: 0 for d in directions}
    # 20% תקיפה
    weights[5] = 5
    # 20% לכיוון האחרון
    if last_direction in directions and last_direction!=5:
        weights[last_direction] += 20
    # חישוב הפוך למרחק – ככל שקרוב יותר, הסיכוי גבוה יותר
    total = abs(dx) + abs(dy)

    if total > 0:
        dx_part = abs(dx) / total
        dy_part = abs(dy) / total

        # חלוקת 60% בין צירי X ו-Y
        if dx > 0:
            weights[4] += int(60 * dx_part)  # שמאלה
        elif dx < 0:
            weights[2] += int(60 * dx_part)  # ימינה
        if dy > 0:
            weights[1] += int(60 * dy_part)  # למעלה
        elif dy < 0:
            weights[3] += int(60 * dy_part)  # למטה
    print(weights)
    total_weight = sum(weights.values())
    if total_weight == 0:
        return random.choice(directions)  # fallback

    normalized_weights = {k: (v / total_weight * 100) for k, v in weights.items()}
    print(normalized_weights)
    # בחירה לפי משקל
    roll = random.randint(1, 100)
    cumulative = 0
    for direction in directions:
        cumulative += weights[direction]
        if roll <= cumulative:
            return direction
    return max(normalized_weights, key=normalized_weights.get)

def save_tuples(tuples):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    for t in tuples:
        if len(t) == 4:
            # עדכון מיקום וכיוון
            x, y, bot_id, direction = t
            cursor.execute(
                "UPDATE bots SET position_x = ?, position_y = ?, last_direction = ? WHERE bot_id = ?",
                (x, y, direction, bot_id)
            )
        elif len(t) == 2:
            # עדכון כיוון בלבד (למשל אחרי תקיפה)
            bot_id, direction = t
            cursor.execute(
                "UPDATE bots SET last_direction = ? WHERE bot_id = ?",
                (direction, bot_id)
            )
    conn.commit()
    conn.close()

def bot_action(action, bot):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    x, y = bot['position_x'], bot['position_y']
    did_something = False

    if action in [1, 2, 3, 4]:
        if action == 1: #up
            y -= 7
        elif action == 2: #right
            x += 7
        elif action == 3: #down
            y += 7
        elif action == 4: #left
            x -= 7
        cursor.execute(
            "UPDATE bots SET position_x = ?, position_y = ? WHERE bot_id = ?",
            (x, y, bot['bot_id'])
        )
    elif action == 5:
        cursor.execute("SELECT * FROM players WHERE status = 'active'")
        players = cursor.fetchall()
        for player in players:
            player_id = player['player_id']
            player_x, player_y = player['position_x'], player['position_y']
            distance = hypot(x - player_x, y - player_y)
            if distance <= 200:
                new_health = max(0, player['health'] - 10)
                cursor.execute(
                    "UPDATE players SET health = ? WHERE player_id = ?",
                    (new_health, player_id)
                )
                print(f"Bot {bot['bot_id']} attacked Player {player_id}, new health: {new_health}")
                did_something = True
                break

    # תמיד נעדכן את last_direction, גם אם לא בוצעה פעולה
    cursor.execute(
        "UPDATE bots SET last_direction = ? WHERE bot_id = ?",
        (action, bot['bot_id'])
    )

    conn.commit()
    conn.close()

    # נחזיר בהתאם לסוג הפעולה
    if action in [1, 2, 3, 4]:
        print(f"Returning from bot_action: {(x, y, bot['bot_id'], action)}")
        return x, y, bot['bot_id'], action
    else:
        return bot['bot_id'], action

def update_specific_bot(action,bot_id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    print(bot_id)
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
                    conn.commit()
                    print(f"Bot {bot_id} attacked Player {player_id}, new health: {new_health}")
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


def calculate_dx_dy(bot_x,bot_y,player_x,player_y):
    dx = bot_x - player_x
    dy = bot_y - player_y
    return dx, dy

def get_all_bots():
    print(f"get_all_bots start: {datetime.datetime.now()}")
    conn = sqlite3.connect("../DATABASE_GAME.db")
    conn.row_factory = sqlite3.Row  # מאפשר גישה לפי שמות
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bots")
    rows = cursor.fetchall()
    conn.close()
    print(f"get_all_bots end: {datetime.datetime.now()}")
    print([dict(row) for row in rows])
    return [dict(row) for row in rows]  # הפיכת כל Row ל־dict

def get_all_bot_ids():
    conn = sqlite3.connect("../DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("SELECT bot_id FROM bots")
    bot_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return bot_ids

def get_all_players():
    start = time.time()
    conn = sqlite3.connect("../DATABASE_GAME.db")
    cursor = conn.cursor()
    # כל השחקנים הפעילים
    cursor.execute("SELECT player_id, position_x, position_y FROM players WHERE status = 'active'")
    players = cursor.fetchall()
    conn.close()
    print(f"get_closest_player:{time.time() - start}")
    return players

def get_closest_player(bot_x, bot_y,players):
    min_dist = float('inf')
    closest_player_id = None
    play_x=None
    play_y=None
    for player_id, player_x, player_y in players:
        dx = bot_x - player_x
        dy = bot_y - player_y
        dist = (dx**2 + dy**2)**0.5
        if dist < min_dist:
            min_dist = dist
            closest_player_id = player_id
            play_x=player_x
            play_y = player_y
    return closest_player_id,play_x,play_y


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
