import sqlite3

def add_player(username):
    server_counts = {}
    for server_id in range(1, 5):  # סרברים 1 עד 4
        server_counts[server_id] = count_users_on_server(server_id)
    least_loaded_server = min(server_counts, key=server_counts.get)
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_servers (username, server_id) VALUES (?, ?)",
                   (username, least_loaded_server))
    conn.commit()
    conn.close()

    print(f"המשתמש {username} שובץ לשרת מספר {least_loaded_server}")
    return least_loaded_server

def count_users_on_server(server_id):
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM user_servers WHERE server_id = ?", (server_id,))
    count = cursor.fetchone()[0]

    conn.close()
    return count

add_player("mordy")