import sqlite3
import bcrypt
import random

conn = sqlite3.connect("DATABASE_GAME.db")
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

cursor.execute("""
CREATE TABLE bots (
    bot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    health INTEGER DEFAULT 100,
    bot_type TEXT CHECK(bot_type IN ('melee', 'ranged')) NOT NULL,
    last_direction_time INTEGER DEFAULT 0,
    last_attack_time INTEGER DEFAULT 0,
    last_direction INTEGER DEFAULT NULL
);
""")

cursor.execute("""
CREATE TABLE items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,            
    x INTEGER NOT NULL,            
    y INTEGER NOT NULL,            
    slot_index INTEGER,            
    quantity INTEGER DEFAULT 1     
);
""")

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

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password

for _ in range(100):
    position_x = random.randint(0, 50000)
    position_y = random.randint(0, 50000)
    health = 100
    bot_type = random.choice(['melee', 'ranged'])
    last_direction_time = 0
    last_attack_time = 0
    last_direction = 1
    cursor.execute("""
        INSERT INTO bots (position_x, position_y, health, bot_type, last_direction_time, last_attack_time,last_direction)
        VALUES (?, ?, ?, ?, ?, ?,?)
    """, (position_x, position_y, health, bot_type, last_direction_time, last_attack_time,last_direction))

nearby_positions = [
    (10, 90),
    (30, 110),
    (200, 157)
]

for pos_x, pos_y in nearby_positions:
    health = 100
    bot_type = random.choice(['melee', 'ranged'])
    last_direction_time = 0
    last_attack_time = 0
    last_direction = 1
    cursor.execute("""
        INSERT INTO bots (position_x, position_y, health, bot_type, last_direction_time, last_attack_time, last_direction)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (pos_x, pos_y, health, bot_type, last_direction_time, last_attack_time, last_direction))

map_objects_json = {
    "On map objects": {
        "apple_tree": {"file": "Apple_Tree.jpg", "rotation": False},
        "tree": {"file": "Tree.jpg", "rotation": False},
        "blueberry_bush": {"file": "Blueberry_Bush.jpg", "rotation": False},
        "bush": {"file": "Bush.jpg", "rotation": False},
        "grass": {"file": "Grass.jpg", "rotation": False},
        "blue_flower": {"file": "Blue_Flower.jpg", "rotation": False},
        "pink_flower": {"file": "Pink_Flower.jpg", "rotation": False},
        "purple_flower": {"file": "Purple_Flower.jpg", "rotation": False},
        "red_flower": {"file": "Red_Flower.jpg", "rotation": False},
        "yellow_flower": {"file": "Yellow_Flower.jpg", "rotation": False}
    }
}

# נניח שהמפה מחולקת ל-40 מסכים (5x8 או 8x5 לדוגמה)
screens_x = 8
screens_y = 5
screen_width = 5000   # גודל מסך אחד
screen_height = 5000
objects_per_screen = 12

object_keys = list(map_objects_json["On map objects"].keys())

# הוספת אובייקטים רנדומליים לכל מסך
for screen_y in range(screens_y):
    for screen_x in range(screens_x):
        for _ in range(objects_per_screen):
            obj_name = random.choice(object_keys)
            obj_data = map_objects_json["On map objects"][obj_name]

            # חישוב מיקום רנדומלי בתוך גבולות המסך הזה
            x = screen_x * screen_width + random.randint(0, screen_width)
            y = screen_y * screen_height + random.randint(0, screen_height)

            cursor.execute("""
                INSERT INTO map_objects (name, file, rotation, position_x, position_y)
                VALUES (?, ?, ?, ?, ?)
            """, (obj_name, obj_data["file"], obj_data["rotation"], x, y))
            conn.commit()

print("✅ Database successfully created with map object positions, inventory table, and speed column in players!")
