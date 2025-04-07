import sqlite3
import bcrypt

# יצירת חיבור למסד הנתונים
conn = sqlite3.connect("DATABASE_GAME.db")
cursor = conn.cursor()

# מחיקת טבלאות ישנות אם קיימות
cursor.execute("DROP TABLE IF EXISTS players;")
cursor.execute("DROP TABLE IF EXISTS items;")
cursor.execute("DROP TABLE IF EXISTS bots;")
cursor.execute("DROP TABLE IF EXISTS map_objects;")  # גם את זו אם קיימת

# יצירת טבלת players
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

# יצירת טבלת bots
cursor.execute('''
CREATE TABLE IF NOT EXISTS bots (
    bot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    health INTEGER DEFAULT 100,
    bot_type TEXT CHECK(bot_type IN ('melee', 'ranged')) NOT NULL,
    last_direction_time INTEGER DEFAULT 0
);
''')

# יצירת טבלת items
cursor.execute("""
CREATE TABLE items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);
""")

# יצירת טבלת map_objects
cursor.execute("""
CREATE TABLE IF NOT EXISTS map_objects (
    object_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    file TEXT NOT NULL,
    rotation BOOLEAN NOT NULL
);
""")

# פונקציה להצפנת סיסמא
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password

# פונקציה לבדוק סיסמא
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

# הכנסת map objects מה-JSON
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

for code, data in map_objects_json["On map objects"].items():
    cursor.execute("""
    INSERT INTO map_objects (code, file, rotation) VALUES (?, ?, ?);
    """, (code, data["file"], data["rotation"]))

conn.commit()
conn.close()

print("✅ Database successfully created with secure password storage and map objects!")
