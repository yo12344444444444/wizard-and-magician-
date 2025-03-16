import sqlite3
import bcrypt

# Create a connection to the database
conn = sqlite3.connect("DATABASE_GAME.db")
cursor = conn.cursor()

# Delete old tables if they exist
cursor.execute("DROP TABLE IF EXISTS players;")
cursor.execute("DROP TABLE IF EXISTS items;")

# Create the players table with username and securely stored password
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

# Create the items table
cursor.execute("""
CREATE TABLE items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);
""")


def hash_password(password):
    """Function to hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password


def verify_password(username, password):
    """Function to verify if the username and password match"""
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM players WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        stored_hash = result[0]
        return bcrypt.checkpw(password.encode(), stored_hash.encode())
    return False


# Insert players with hashed passwords
cursor.execute(
    "INSERT INTO players (username, password_hash, position_x, position_y, health, coins, status) VALUES (?, ?, ?, ?, ?, ?, ?);",
    ("Player1", hash_password("password123"), 21600, 38400, 100, 200, 'active'))

cursor.execute(
    "INSERT INTO players (username, password_hash, position_x, position_y, health, coins, status) VALUES (?, ?, ?, ?, ?, ?, ?);",
    ("Player2", hash_password("mysecurepass"), 21600, 38400, 100, 200, 'active'))

# Insert example items for players
cursor.execute("INSERT INTO items (player_id, item_name, quantity) VALUES (1, 'Sword', 1);")
cursor.execute("INSERT INTO items (player_id, item_name, quantity) VALUES (1, 'HealthPotion', 3);")
cursor.execute("INSERT INTO items (player_id, item_name, quantity) VALUES (2, 'Bow', 1);")

# Save changes and close the connection
conn.commit()
conn.close()

print("✅ Database successfully created with secure password storage!")
