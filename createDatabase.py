import sqlite3
import bcrypt
import random

# יצירת חיבור למסד הנתונים
conn = sqlite3.connect("DATABASE_GAME.db")
cursor = conn.cursor()

# מחיקת טבלאות ישנות אם קיימות
cursor.execute("DROP TABLE IF EXISTS players;")
cursor.execute("DROP TABLE IF EXISTS items;")
cursor.execute("DROP TABLE IF EXISTS bots;")
cursor.execute("DROP TABLE IF EXISTS map_objects;")  # גם את זו אם קיימת

# טבלת players
cursor.execute("""
CREATE TABLE players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    position_x INTEGER NOT NULL DEFAULT 0,
    position_y INTEGER NOT NULL DEFAULT 0,
    health INTEGER NOT NULL DEFAULT 100,
    coins INTEGER NOT NULL DEFAULT 200,
    status TEXT NOT NULL DEFAULT 'active'
);
""")

# טבלת bots
cursor.execute('''
CREATE TABLE bots (
    bot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    health INTEGER DEFAULT 100,
    bot_type TEXT CHECK(bot_type IN ('melee', 'ranged')) NOT NULL,
    last_direction_time INTEGER DEFAULT 0
);
''')

# טבלת items
cursor.execute("""
CREATE TABLE items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);
""")

# טבלת map_objects עם מיקום!
cursor.execute("""
CREATE TABLE map_objects (
    object_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    file TEXT NOT NULL,
    rotation BOOLEAN NOT NULL,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL
);
""")

# הצפנת סיסמא
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password

# אימות סיסמא
def verify_password(username, password):
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM players WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        stored_hash = result[0]
        return bcrypt.checkpw(password.encode(), stored_hash.encode())
    return False

# הכנסת שחקנים
cursor.execute(
    "INSERT INTO players (username, password_hash, position_x, position_y, health, coins, status) VALUES (?, ?, ?, ?, ?, ?, ?);",
    ("Player1", hash_password("password123"), 21600, 38400, 100, 200, 'active'))

cursor.execute(
    "INSERT INTO players (username, password_hash, position_x, position_y, health, coins, status) VALUES (?, ?, ?, ?, ?, ?, ?);",
    ("Player2", hash_password("mysecurepass"), 21600, 38400, 100, 200, 'active'))

# הכנסת חפצים
cursor.execute("INSERT INTO items (player_id, item_name, quantity) VALUES (1, 'Sword', 1);")
cursor.execute("INSERT INTO items (player_id, item_name, quantity) VALUES (1, 'HealthPotion', 3);")
cursor.execute("INSERT INTO items (player_id, item_name, quantity) VALUES (2, 'Bow', 1);")

# הכנסת בוטים
cursor.execute("INSERT INTO bots (bot_type, position_x, position_y, health) VALUES (?, ?, ?, ?);",
               ("melee", 22000, 39000, 100))
cursor.execute("INSERT INTO bots (bot_type, position_x, position_y, health) VALUES (?, ?, ?, ?);",
               ("ranged", 23000, 40000, 80))
cursor.execute("INSERT INTO bots (bot_type, position_x, position_y, health) VALUES (?, ?, ?, ?);",
               ("melee", 24000, 38000, 120))

# Add players near the main player and far away
cursor.execute("""
INSERT INTO players (username, password_hash, position_x, position_y, health, coins, status)
VALUES 
('player1', 'hashed_password_1', 100, 100, 100, 200, 'active'),
('player2', 'hashed_password_2', 500, 500, 100, 200, 'active'),
('player3', 'hashed_password_3', 1500, 1500, 100, 200, 'active');
""")

# Add bots near the main player and far away
cursor.execute("""
INSERT INTO bots (position_x, position_y, health, bot_type, last_direction_time)
VALUES
(120, 120, 80, 'melee', 1587001234),
(300, 300, 80, 'ranged', 1587001244),
(1500, 1500, 80, 'melee', 1587001254);
""")

# Add map objects near the main player and far away
cursor.execute("""
INSERT INTO map_objects (code, file, rotation, position_x, position_y)
VALUES
('tree', 'tree.png', 0, 100, 100),
('rock', 'rock.png', 0, 200, 200),
('bush', 'bush.png', 1, 1500, 1500);
""")
conn.commit()

# JSON כמו שהבאת קודם
map_objects_json = {
    "On map objects": {
        "a": {"file": "Apple_Tree.jpg", "rotation": False},
        "b": {"file": "Tree.jpg", "rotation": False},
        "c": {"file": "Blueberry_Bush.jpg", "rotation": False},
        "d": {"file": "Bush.jpg", "rotation": False},
        "e": {"file": "Grass.jpg", "rotation": False},
        "f": {"file": "Iron.jpg", "rotation": False},
        "g": {"file": "Gold.jpg", "rotation": False},
        "h": {"file": "Stones.jpg", "rotation": False},
        "i": {"file": "Blue_Flower.jpg", "rotation": False},
        "j": {"file": "Pink_Flower.jpg", "rotation": False},
        "k": {"file": "Purple_Flower.jpg", "rotation": False},
        "l": {"file": "Red_Flower.jpg", "rotation": False},
        "m": {"file": "Yellow_Flower.jpg", "rotation": False}
    }
}

conn = sqlite3.connect("../DATABASE_GAME.db")
cursor = conn.cursor()

for key, obj in map_objects_json["On map objects"].items():
    x = random.randint(0, 1000)
    y = random.randint(0, 1000)
    cursor.execute("""
        INSERT INTO map_objects (code, file, rotation, position_x, position_y)
        VALUES (?, ?, ?, ?, ?)
    """, (key, obj["file"], obj["rotation"], x, y))

conn.commit()
conn.close()
print("Objects inserted.")

# לדוגמה - מיקומים בין 21000-25000 ב-x ו-38000-42000 ב-y
x_positions = [21500, 22000, 22500, 23000, 23500, 24000, 24500]
y_positions = [38500, 39000, 39500, 40000, 40500, 41000, 41500]

for idx, (code, data) in enumerate(map_objects_json["On map objects"].items()):
    position_x = x_positions[idx % len(x_positions)]
    position_y = y_positions[idx % len(y_positions)]
    cursor.execute("""
    INSERT INTO map_objects (code, file, rotation, position_x, position_y)
    VALUES (?, ?, ?, ?, ?);
    """, (code, data["file"], data["rotation"], position_x, position_y))

conn.commit()
conn.close()

print("✅ Database successfully created with map object positions!")
