import sqlite3
import bcrypt
import random

conn = sqlite3.connect("/app/DATABASE_GAME.db")
cursor = conn.cursor()

# מחיקת טבלאות ישנות אם קיימות
cursor.execute("DROP TABLE IF EXISTS players;")
cursor.execute("DROP TABLE IF EXISTS items;")
cursor.execute("DROP TABLE IF EXISTS bots;")
cursor.execute("DROP TABLE IF EXISTS map_objects;")
cursor.execute("DROP TABLE IF EXISTS inventory;")  # נוספה

# טבלת players עם עמודת מהירות
cursor.execute("""
CREATE TABLE players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    position_x INTEGER NOT NULL DEFAULT 0,
    position_y INTEGER NOT NULL DEFAULT 0,
    health INTEGER NOT NULL DEFAULT 100,
    coins INTEGER NOT NULL DEFAULT 200,
    status TEXT NOT NULL DEFAULT 'active',
    speed INTEGER NOT NULL DEFAULT 3,
    last_attack_time DATETIME
)
""")


# טבלת bots
cursor.execute("""
CREATE TABLE bots (
    bot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    health INTEGER DEFAULT 100,
    bot_type TEXT CHECK(bot_type IN ('melee', 'ranged')) NOT NULL,
    last_direction_time INTEGER DEFAULT 0,
    last_attack_time INTEGER DEFAULT 0
);
""")

# טבלת items (עודכנה)
cursor.execute("""
CREATE TABLE items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    slot_index INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);
""")

# טבלת map_objects
cursor.execute("""
CREATE TABLE map_objects (
    object_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    file TEXT NOT NULL,
    rotation BOOLEAN NOT NULL,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL
);
""")

# ✅ טבלת inventory
cursor.execute("""
CREATE TABLE inventory (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    slot_index INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);
""")
cursor.execute("""
CREATE UNIQUE INDEX IF NOT EXISTS unique_inventory_player_object 
ON inventory (player_id, name);
""")

# סיסמאות
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password

# הכנסת שחקנים עם מהירות
cursor.execute(
    "INSERT INTO players (username, password_hash, position_x, position_y, health, coins, status, speed) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
    ("Player1", hash_password("password123"), 21600, 38400, 100, 200, 'active', 1))
cursor.execute(
    "INSERT INTO players (username, password_hash, position_x, position_y, health, coins, status, speed) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
    ("Player2", hash_password("mysecurepass"), 21600, 38400, 100, 200, 'active', 1))


# פריטים
cursor.execute("INSERT INTO items (player_id, name, slot_index, quantity) VALUES (1, 'Sword', 0, 1);")
cursor.execute("INSERT INTO items (player_id, name, slot_index, quantity) VALUES (1, 'HealthPotion', 1, 3);")
cursor.execute("INSERT INTO items (player_id, name, slot_index, quantity) VALUES (2, 'Bow', 0, 1);")

# בוטים
cursor.execute("INSERT INTO bots (bot_type, position_x, position_y, health) VALUES (?, ?, ?, ?);",
               ("melee", 300, 300, 100))
cursor.execute("INSERT INTO bots (bot_type, position_x, position_y, health) VALUES (?, ?, ?, ?);",
               ("ranged", 120, 120, 100))
cursor.execute("INSERT INTO bots (bot_type, position_x, position_y, health) VALUES (?, ?, ?, ?);",
               ("melee", 24000, 38000, 120))

# שחקנים נוספים
cursor.execute("""
INSERT INTO players (username, password_hash, position_x, position_y, health, coins, status, speed)
VALUES 
('player1', 'hashed_password_1', 100, 100, 100, 200, 'active', 1),
('player2', 'hashed_password_2', 500, 500, 100, 200, 'active', 1),
('player3', 'hashed_password_3', 1500, 1500, 100, 200, 'active', 1);
""")

# בוטים נוספים
cursor.execute("""
INSERT INTO bots (position_x, position_y, health, bot_type, last_direction_time)
VALUES
(120, 120, 80, 'melee', 1587001234),
(300, 300, 80, 'ranged', 1587001244),
(1500, 1500, 80, 'melee', 1587001254);
""")

# אובייקטים
cursor.execute("""
INSERT INTO map_objects (name, file, rotation, position_x, position_y)
VALUES
('tree', 'tree.png', 0, 100, 100),
('rock', 'rock.png', 0, 200, 200),
('bush', 'bush.png', 1, 1500, 1500);
""")

map_objects_json = {
    "On map objects": {
        "apple_tree": {"file": "Apple_Tree.jpg", "rotation": False},
        "tree": {"file": "Tree.jpg", "rotation": False},
        "blueberry_bush": {"file": "Blueberry_Bush.jpg", "rotation": False},
        "bush": {"file": "Bush.jpg", "rotation": False},
        "grass": {"file": "Grass.jpg", "rotation": False},
        "iron_sword": {"file": "Iron_Sword.jpg", "rotation": False},
        "gold_sword": {"file": "Gold_Sword.jpg", "rotation": False},
        "stone_sword": {"file": "Stones_Sword.jpg", "rotation": False},
        "blue_flower": {"file": "Blue_Flower.jpg", "rotation": False},
        "pink_flower": {"file": "Pink_Flower.jpg", "rotation": False},
        "purple_flower": {"file": "Purple_Flower.jpg", "rotation": False},
        "red_flower": {"file": "Red_Flower.jpg", "rotation": False},
        "yellow_flower": {"file": "Yellow_Flower.jpg", "rotation": False}
    }
}

# יצירת אובייקטים אקראיים
for key, obj in map_objects_json["On map objects"].items():
    x = random.randint(0, 1000)
    y = random.randint(0, 1000)
    cursor.execute("""
        INSERT INTO map_objects (name, file, rotation, position_x, position_y)
        VALUES (?, ?, ?, ?, ?)
    """, (key, obj["file"], obj["rotation"], x, y))

# ✅ הוספת אובייקט מיוחד בנקודה (0, 0)
cursor.execute("""
    INSERT INTO map_objects (name, file, rotation, position_x, position_y)
    VALUES (?, ?, ?, ?, ?)
""", ('rock', 'rock.png', False, 0, 1))

# הוספת אובייקטים עם מיקומים קבועים
x_positions = [21500, 22000, 22500, 23000, 23500, 24000, 24500]
y_positions = [38500, 39000, 39500, 40000, 40500, 41000, 41500]

for idx, (code, data) in enumerate(map_objects_json["On map objects"].items()):
    position_x = x_positions[idx % len(x_positions)]
    position_y = y_positions[idx % len(y_positions)]
    cursor.execute("""
    INSERT INTO map_objects (name, file, rotation, position_x, position_y)
    VALUES (?, ?, ?, ?, ?);
    """, (code, data["file"], data["rotation"], position_x, position_y))

conn.commit()
conn.close()

print("✅ Database successfully created with map object positions, inventory table, and speed column in players!")
