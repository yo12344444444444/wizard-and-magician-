import sqlite3

# יצירת חיבור למסד הנתונים
conn = sqlite3.connect("DATABASE_GAME_MAIN.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS user_servers;")
cursor.execute("DROP TABLE IF EXISTS servers_ips;")

# יצירת טבלה בשם user_servers עם עמודות: username ו-server_id
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_servers (
    username TEXT PRIMARY KEY,
    server_id INTEGER NOT NULL
)
""")

# יצירת טבלה בשם servers_ips עם עמודות: server_ip ו-server_num
cursor.execute("""
CREATE TABLE IF NOT EXISTS servers_ips (
    server_ip TEXT NOT NULL,  -- הוספת סוג נתונים (TEXT לדוגמה)
    server_num INTEGER NOT NULL
)
""")

def add_user(username, server_id):
    if server_id not in [1, 2, 3, 4]:
        print("מספר סרבר לא תקין.")
        return

    conn = sqlite3.connect("DATABASE_GAME_MAIN.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO user_servers (username, server_id) VALUES (?, ?)", (username, server_id))
        conn.commit()
        print(f"המשתמש {username} נוסף עם סרבר {server_id}")
    except sqlite3.IntegrityError:
        print("המשתמש כבר קיים במערכת.")
    finally:
        conn.close()

def add_local_servers():
    """מוסיפה 4 סרברים עם IP '127.0.0.1' לטבלה servers_ips."""
    conn = sqlite3.connect("DATABASE_GAME_MAIN.db")
    cursor = conn.cursor()

    try:
        for i in range(1, 5):
            cursor.execute("INSERT INTO servers_ips (server_ip, server_num) VALUES (?, ?)", ('192.168.1.79', i))
        conn.commit()
        print("4 סרברים מקומיים נוספו לטבלה servers_ips.")
    except sqlite3.Error as e:
        print(f"שגיאה בהוספת סרברים: {e}")
        conn.rollback()
    finally:
        conn.close()

# שימוש
add_user("adi", 2)
add_user("yael", 2)
add_user("naama", 2)
add_user("bar", 2)
add_local_servers()

# שמירה וסגירת החיבור
conn.commit()
conn.close()

print("added 4 servers with 192.168.1.79")
print("Table 'user_servers' created successfully.")
print("Table 'servers_ips' created successfully.")