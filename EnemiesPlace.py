import sqlite3

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

def get_objects_near_player(player_id):
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()

    # קבלת מיקום השחקן לפי ID
    cursor.execute("SELECT position_x, position_y FROM players WHERE player_id = ?", (player_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return []

    player_x, player_y = result

    # חישוב גבולות המסך שסביב השחקן
    half_width = SCREEN_WIDTH // 2
    half_height = SCREEN_HEIGHT // 2

    min_x = player_x - half_width
    max_x = player_x + half_width
    min_y = player_y - half_height
    max_y = player_y + half_height

    # שליפת כל האובייקטים שנמצאים בגבולות המסך
    cursor.execute("""
        SELECT object_id, code, position_x, position_y
        FROM map_objects
        WHERE position_x BETWEEN ? AND ?
        AND position_y BETWEEN ? AND ?
    """, (min_x, max_x, min_y, max_y))

    objects = cursor.fetchall()
    conn.close()

    # החזרת הרשימה בפורמט נוח (רשימת מילונים)
    return [
        {
            "object_id": obj[0],
            "code": obj[1],
            "position_x": obj[2],
            "position_y": obj[3]
        }
        for obj in objects
    ]


def main():
    try:
        player_id = int(input("🔎 הכנס את ה-ID של השחקן: "))
        objects = get_objects_near_player(player_id)
        if not objects:
            print("לא נמצאו אובייקטים במסך של השחקן.")
        else:
            print(f"\n📦 נמצאו {len(objects)} אובייקטים במסך של השחקן:")
            for obj in objects:
                print(f"  ➤ ID: {obj['object_id']}, סוג: {obj['code']}, מיקום: ({obj['position_x']}, {obj['position_y']})")
    except ValueError:
        print("⚠️ ה-ID חייב להיות מספר שלם.")


if __name__ == "__main__":
    main()
