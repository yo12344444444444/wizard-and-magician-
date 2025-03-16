import socket
import sqlite3
import pickle  # 📦 נוסיף את pickle כדי לארוז את הנתונים

IP = '127.0.0.1'
PORT = 8825
DEFAULT_BUFFER_SIZE = 1024


def get_players_from_db():
    """שליפת נתוני שחקנים ממסד הנתונים"""
    conn = sqlite3.connect('DATABASE_GAME.db')  # התחברות למסד הנתונים
    cursor = conn.cursor()
    cursor.execute("SELECT ip_address, position_x, position_y, health FROM players")
    players = cursor.fetchall()
    conn.close()
    return players


def handle_client(packed_data, server_socket, client_addr):
    """
    קבלת בקשה ושליחת מידע לשחקן
    """
    try:
        players = get_players_from_db()  # שליפת נתונים מהמסד
        response = [{"ip": p[0], "x": p[1], "y": p[2], "health": p[3]} for p in players]  # המרת הנתונים למילון
        packed_response = pickle.dumps(response)  # 📦 שימוש ב-pickle לאריזה
        print(f"📡 Sending data to client {client_addr}: {response}")  # ✅ הדפסה לפני שליחה
        server_socket.sendto(packed_response, client_addr)  # שליחת תשובה ללקוח
    except Exception as ex:
        print(f"Error handling client: {str(ex)}")


def udp_server():
    """הפעלת שרת ה-UDP"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))
    print(f"✅ UDP Server running on {IP}:{PORT}")

    while True:
        try:
            packed_data, client_addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            handle_client(packed_data, server_socket, client_addr)
        except Exception as ex:
            print(f"Client exception: {str(ex)}")


def main():
    udp_server()


if __name__ == "__main__":
    main()
