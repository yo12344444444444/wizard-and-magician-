import sqlite3
import bcrypt
import random

conn = sqlite3.connect("/app/database/DATABASE_GAME.db")
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
# הגדרות מסך
screen_width = 900
screen_height = 700
screens_x = 8
screens_y = 5
objects_per_screen = 12
player_screen_x = 0 // screen_width
player_screen_y = 100 // screen_height

# הוספת בוטים: קודם כל נוסיף 8 למסך השחקן
for _ in range(8):
    pos_x = random.randint(player_screen_x * screen_width, (player_screen_x + 1) * screen_width - 1)
    pos_y = random.randint(player_screen_y * screen_height, (player_screen_y + 1) * screen_height - 1)
    bot_type = random.choice(['melee', 'ranged'])
    cursor.execute("""
        INSERT INTO bots (position_x, position_y, health, bot_type, last_direction_time, last_attack_time, last_direction)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (pos_x, pos_y, 100, bot_type, 0, 0, 1))

# נוסיף עוד 100 בוטים רנדומליים במסכים אחרים
for _ in range(100):
    pos_x = random.randint(0, screen_width * screens_x - 1)
    pos_y = random.randint(0, screen_height * screens_y - 1)

    # לא נשכפל למסך של השחקן
    if pos_x // screen_width == player_screen_x and pos_y // screen_height == player_screen_y:
        continue

    bot_type = random.choice(['melee', 'ranged'])
    cursor.execute("""
        INSERT INTO bots (position_x, position_y, health, bot_type, last_direction_time, last_attack_time, last_direction)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (pos_x, pos_y, 100, bot_type, 0, 0, 1))

# אובייקטים למפה
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
object_keys = list(map_objects_json["On map objects"].keys())

# הוספת לפחות 7 למסך של השחקן
for _ in range(7):
    obj_name = random.choice(object_keys)
    obj_data = map_objects_json["On map objects"][obj_name]
    x = random.randint(player_screen_x * screen_width, (player_screen_x + 1) * screen_width - 1)
    y = random.randint(player_screen_y * screen_height, (player_screen_y + 1) * screen_height - 1)

    cursor.execute("""
        INSERT INTO map_objects (name, file, rotation, position_x, position_y)
        VALUES (?, ?, ?, ?, ?)
    """, (obj_name, obj_data["file"], obj_data["rotation"], x, y))

# מסכים אחרים – רנדומליים
for screen_y in range(screens_y):
    for screen_x in range(screens_x):
        # דלג על המסך של השחקן
        if screen_x == player_screen_x and screen_y == player_screen_y:
            continue
        for _ in range(objects_per_screen):
            obj_name = random.choice(object_keys)
            obj_data = map_objects_json["On map objects"][obj_name]
            x = screen_x * screen_width + random.randint(0, screen_width - 1)
            y = screen_y * screen_height + random.randint(0, screen_height - 1)

            cursor.execute("""
                INSERT INTO map_objects (name, file, rotation, position_x, position_y)
                VALUES (?, ?, ?, ?, ?)
            """, (obj_name, obj_data["file"], obj_data["rotation"], x, y))

conn.commit()
print("✅ Database initialized: player screen includes 8 bots and 7+ objects.")

