import sqlite3

# יצירת חיבור למסד הנתונים
conn = sqlite3.connect("DATABASE_GAME_MAIN.db")
cursor = conn.cursor()

# יצירת טבלה בשם user_servers עם עמודות: username ו-server_id
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_servers (
    username TEXT PRIMARY KEY,
    server_id INTEGER NOT NULL
)
""")

def add_user(username, server_id):
    if server_id not in [1, 2, 3, 4]:
        print("מספר סרבר לא תקין.")
        return

    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO user_servers (username, server_id) VALUES (?, ?)", (username, server_id))
        conn.commit()
        print(f"המשתמש {username} נוסף עם סרבר {server_id}")
    except sqlite3.IntegrityError:
        print("המשתמש כבר קיים במערכת.")
    finally:
        conn.close()

# שימוש
add_user("adi", 2)
add_user("yael", 2)
add_user("naama", 2)
add_user("bar", 2)

# שמירה וסגירת החיבור
conn.commit()
conn.close()

print("Table 'user_servers' created successfully.")
