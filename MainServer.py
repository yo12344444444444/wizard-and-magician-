import socket
import pickle
import sqlite3

DNS_SERVER_IP = '0.0.0.0'
DNS_SERVER_PORT = 8827
DEFAULT_BUFFER_SIZE = 1024

FORWARDING_SERVERS = {
    1: ('127.0.0.1', 8823),  # רבעון 1
    2: ('127.0.0.1', 8824),  # רבעון 2
    3: ('127.0.0.1', 8825),  # רבעון 3
    4: ('127.0.0.1', 8826)   # רבעון 4
}

# התחברות למסד הנתונים עם טיפול בשגיאות
try:
    conn = sqlite3.connect("DATABASE_GAME.db", check_same_thread=False)
    cursor = conn.cursor()
    print(" Successfully connected to the database.")
except sqlite3.Error as e:
    print(f" Error connecting to the database: {e}")
    exit(1)  # יציאה מהתוכנית אם לא ניתן להתחבר למסד הנתונים

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

def get_player_quadrant(player_id):
    """
    מחפש את השחקן במסד הנתונים לפי ה-ID ושולף את הקואורדינטות שלו כדי לקבוע את הרבעון
    """
    try:
        cursor.execute("SELECT x, y FROM players WHERE id = ?", (id,))
        result = cursor.fetchone()
        if result:
            x, y = result
            if x > 0 and y > 0:
                return 1  # רבעון 1
            elif x < 0 and y > 0:
                return 2  # רבעון 2
            elif x < 0 and y < 0:
                return 3  # רבעון 3
            elif x > 0 and y < 0:
                return 4  # רבעון 4
        else:
            print(f" Player ID {player_id} not found in database.")
            return None
    except sqlite3.Error as e:
        print(f" Database error: {e}")
        return None

def request_handler(data, addr):
    """
    מקבל פאקטה מהקליינט, מזהה את השחקן לפי ה-ID ושולח אותו לשרת המשני לפי המיקום במסד הנתונים.
    """
    print(f" Received request from {addr}")
    id = int(data, 2)
    print(id)
    try:
        add_player(id)
        print(f"added player {id} ")
    except Exception as ex:
        print("the player is already exist")

def udp_server(ip, port):
    """
    מפעיל שרת UDP שמאזין לבקשות ומעביר אותן בהתאם למיקום מה-Database.
    """
    print(" Starting UDP forwarder server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))
    print(f" Server started at {ip}:{port}, waiting for data...")

    while True:
        try:
            data, addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            print(f" Received data from {addr}")
            server_socket.sendto(str(1).encode(), addr)
            request_handler(data, addr)
        except Exception as ex:
            print(f" Client exception: {str(ex)}")

def main():
    udp_server(DNS_SERVER_IP, DNS_SERVER_PORT)

if __name__ == '__main__':
    main()
