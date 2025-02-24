import sqlite3
import socket
import pickle

# התחברות למסד הנתונים
conn = sqlite3.connect("DATABASE_GAME.db", check_same_thread=False)
cursor = conn.cursor()
print("Connected to DATABASE_GAME.db successfully")

# הצגת כל הנתונים במסד בעת הפעלת השרת
cursor.execute("SELECT * FROM players;")
players = cursor.fetchall()
print("Players in database at startup:", players)

conn.set_trace_callback(print)  # יציג את כל השאילתות שמתבצעות

# פונקציה לקבלת נתוני שחקן
def get_player_data(username):
    cursor.execute("SELECT username, position_x, position_y, health, coins, status FROM players WHERE username = ?", (username,))
    player_data = cursor.fetchone()
    print(f"Fetched data from DB for {username}: {player_data}")  # בדיקה אם הנתונים נשלפים
    return player_data

# פונקציה לעדכון מיקום שחקן
def update_player_position(username, x, y):
    cursor.execute("UPDATE players SET position_x = ?, position_y = ? WHERE username = ?", (x, y, username))
    conn.commit()
    print(f"Updated position for {username} to ({x}, {y})")

# שליחת נתוני שחקן ללקוח
def send_player_data_to_client(player_data, client_socket, client_addr):
    response = {
        "username": player_data[0],
        "position": (player_data[1], player_data[2]),
        "health": player_data[3],
        "coins": player_data[4],
        "status": player_data[5]
    }
    packed_data = pickle.dumps(response)
    client_socket.sendto(packed_data, client_addr)
    print(f"Sent data to client {client_addr}: {response}")

# טיפול בבקשת לקוח
def handle_client_request(packed_data, client_socket, client_addr):
    try:
        data = pickle.loads(packed_data)
        username = data.get("username")
        action = data.get("action")

        if action == "update_position":
            position = data.get("position")
            if position and len(position) == 2:
                x, y = position
                update_player_position(username, x, y)
                player_data = get_player_data(username)
                send_player_data_to_client(player_data, client_socket, client_addr)
            else:
                response = {"error": "Invalid data format"}
                client_socket.sendto(pickle.dumps(response), client_addr)

        else:
            player_data = get_player_data(username)
            if player_data:
                send_player_data_to_client(player_data, client_socket, client_addr)
            else:
                response = {"error": "Player not found"}
                client_socket.sendto(pickle.dumps(response), client_addr)

    except Exception as ex:
        print(f"Error handling client: {str(ex)}")

# שרת UDP
def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('127.0.0.1', 8822))
    print("Server listening on 127.0.0.1:8822")

    while True:
        try:
            packed_data, client_addr = server_socket.recvfrom(1024)
            print(f"Received data from {client_addr}: {pickle.loads(packed_data)}")
            handle_client_request(packed_data, server_socket, client_addr)
        except Exception as ex:
            print(f"Error receiving data: {str(ex)}")

# הפעלת השרת
if __name__ == "__main__":
    udp_server()
