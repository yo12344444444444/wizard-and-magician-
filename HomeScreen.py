import sqlite3

def authenticate_user(username, password):
    """Checks if the username and password exist in the database and returns the player data if valid"""
    conn = sqlite3.connect('DATABASE_GAME.db')  # Connect to the database
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE username = ? AND password = ?", (username, password))
    player_data = cursor.fetchone()  # Returns the player's data if they exist
    conn.close()

    if player_data:
        return True, player_data  # Player exists, return True and their data
    else:
        return False, None  # Player does not exist

# Example usage:
exists, data = authenticate_user("player1", "securepass123")
if exists:
    print("User exists! Player data:", data)
else:
    print("ncorrect username or password")
