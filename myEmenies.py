import sqlite3

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

def get_objects_near_player(player_id, db_path='game.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # שליפת מיקום השחקן מהטבלה players
    cursor.execute("SELECT POSITION_X, POSITION_Y FROM players WHERE id = ?", (player_id,))
    result = cursor.fetchone()
    if result is None:
        conn.close()
        return []

    player_x, player_y = result

    # חישוב גבולות המסך סביב השחקן
    left = player_x - SCREEN_WIDTH
    right = player_x + SCREEN_WIDTH
    top = player_y - SCREEN_HEIGHT
    bottom = player_y + SCREEN_HEIGHT

    # שליפת כל האובייקטים בתחום הזה
    cursor.execute("""
        SELECT * FROM objects
        WHERE x BETWEEN ? AND ? AND y BETWEEN ? AND ?
    """, (left, right, top, bottom))


    objects = cursor.fetchall()
    conn.close()
    return objects
