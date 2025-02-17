import sqlite3  # Import the SQLite library

# Connect to (or create) the database
conn = sqlite3.connect("game_database.db")
cursor = conn.cursor()


# Create the players table if it does not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    health INTEGER NOT NULL DEFAULT 100,
    status TEXT CHECK(status IN ('alive', 'dead', 'banned')) NOT NULL DEFAULT 'alive',
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0
)
""")

# Add the coins column if it does not exist (only if it's missing from the existing table)
try:
    cursor.execute("ALTER TABLE players ADD COLUMN coins INTEGER NOT NULL DEFAULT 0")
except sqlite3.OperationalError:
    # If the coins column already exists, no action is needed
    pass

# Create the items table
cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT UNIQUE NOT NULL,
    type TEXT CHECK(type IN ('weapon', 'potion', 'armor')) NOT NULL,
    effect INTEGER NOT NULL
)
""")

# Create the player_items table
cursor.execute("""
CREATE TABLE IF NOT EXISTS player_items (
    player_id INTEGER,
    item_id INTEGER,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (item_id) REFERENCES items(item_id),
    PRIMARY KEY (player_id, item_id)
)
""")

# Function to add a new player
def add_player(username, health=100, status="alive", position_x=0, position_y=0, coins=0):
    try:
        cursor.execute("INSERT INTO players (username, health, status, position_x, position_y, coins) VALUES (?, ?, ?, ?, ?, ?)",
                       (username, health, status, position_x, position_y, coins))
        conn.commit()
        print(f"Player '{username}' has been successfully added!")
    except sqlite3.IntegrityError:
        print(f"Username '{username}' already exists!")

# Function to display all players
def show_players():
    cursor.execute("SELECT * FROM players")
    players = cursor.fetchall()
    for player in players:
        print(player)

# Function to update a player's health
def update_health(username, new_health):
    cursor.execute("UPDATE players SET health = ? WHERE username = ?", (new_health, username))
    conn.commit()
    print(f"Player '{username}' health updated to {new_health}")

# Function to update a player's coins
def update_coins(username, amount):
    cursor.execute("UPDATE players SET coins = coins + ? WHERE username = ?", (amount, username))
    conn.commit()
    print(f"Player '{username}' coins updated by {amount}")

# Function to delete a player
def delete_player(username):
    cursor.execute("DELETE FROM players WHERE username = ?", (username,))
    conn.commit()
    print(f"Player '{username}' has been deleted!")

# Function to add an item
def add_item(item_name, item_type, effect):
    try:
        cursor.execute("INSERT INTO items (item_name, type, effect) VALUES (?, ?, ?)",
                       (item_name, item_type, effect))
        conn.commit()
        print(f"Item '{item_name}' has been successfully added!")
    except sqlite3.IntegrityError:
        print(f"Item '{item_name}' already exists!")

# Function to assign an item to a player
def assign_item_to_player(username, item_name, quantity=1):
    cursor.execute("SELECT player_id FROM players WHERE username = ?", (username,))
    player = cursor.fetchone()
    cursor.execute("SELECT item_id FROM items WHERE item_name = ?", (item_name,))
    item = cursor.fetchone()
    if player and item:
        cursor.execute("""
        INSERT INTO player_items (player_id, item_id, quantity) 
        VALUES (?, ?, ?) 
        ON CONFLICT(player_id, item_id) DO UPDATE SET quantity = quantity + ?
        """, (player[0], item[0], quantity, quantity))
        conn.commit()
        print(f"Item '{item_name}' assigned to '{username}'")
    else:
        print("Invalid player or item!")

add_player("Player1", health=90, position_x=10, position_y=5, coins=100)
add_player("Player2", health=50, position_x=3, position_y=8, coins=200)
add_item("Sword", "weapon", 20)
add_item("Health Potion", "potion", 50)
assign_item_to_player("Player1", "Sword", 1)
show_players()
update_health("Player1", 75)
delete_player("Player2")
show_players()

conn.close()
