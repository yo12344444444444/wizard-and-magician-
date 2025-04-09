import socket
import sqlite3

DNS_SERVER_IP = '0.0.0.0'
DNS_SERVER_PORT = 8827
DEFAULT_BUFFER_SIZE = 1024

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

def get_user_server(username):
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("SELECT server_id FROM user_servers WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_server_ip(server_id):
    conn = sqlite3.connect("DATABASE_GAME.db")
    cursor = conn.cursor()
    cursor.execute("SELECT server_ip FROM servers_ips WHERE server_num = ?", (server_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def check_user_and_get_ip_bits(username):
    """
    בודקת אם משתמש קיים בטבלת user_servers.
    אם קיים, שולפת את ה-server_id שלו, מקבלת את ה-IP מטבלת servers_ips
    ומחזירה 1 ואת כמות הביטים של שני המספרים האחרונים ב-IP.
    אם לא קיים, מחזירה 0 ו-0.
    """
    try:
        conn = sqlite3.connect("DATABASE_GAME.db")
        cursor = conn.cursor()

        # בדוק אם המשתמש קיים
        cursor.execute("SELECT server_id FROM user_servers WHERE username = ?", (username,))
        user_data = cursor.fetchone()

        if user_data:
            server_id = user_data[0]
            # קבל את ה-IP מטבלת servers_ips
            cursor.execute("SELECT server_ip FROM servers_ips WHERE server_num = ?", (server_id,))
            ip_data = cursor.fetchone()

            if ip_data:
                ip_address = ip_data[0]
                parts = ip_address.split('.')
                if len(parts) == 4:
                    last_two_octets = parts[-2:]
                    bits_last_two_octets = len(''.join(format(int(octet), '08b') for octet in last_two_octets))
                    conn.close()
                    return 1, bits_last_two_octets
                else:
                    print(f"Error: Invalid IP address format in database for server {server_id}: {ip_address}")
                    conn.close()
                    return 1, 0  # משתמש קיים, אך IP לא תקין, החזר 0 ביטים
            else:
                print(f"Error: Could not retrieve IP address for server {server_id} from database.")
                conn.close()
                return 1, 0  # משתמש קיים, אך אין IP לשרת, החזר 0 ביטים
        else:
            conn.close()
            return 0, 0  # משתמש לא קיים

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 0, 0
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def request_handler(data, addr):
    """
    מקבל פאקטה מהקליינט, מזהה את השחקן לפי ה-ID ובודק אם קיים.
    שולח לקליינט את המידע שהוחזר מהפונקציה check_user_and_get_ip_bits.
    """
    print(f" Received request from {addr}")
    try:
        player_id = str(int(data, 2))  # המרת הביטים ל-ID (מחרוזת)
        exists, ip_bits = check_user_and_get_ip_bits(player_id)
        response = f"{exists}{ip_bits}".encode()
        print(f" Sending response to {addr}: {response}")
        server_socket.sendto(response, addr)

        if not exists:
            # אם המשתמש לא קיים, הוסף אותו
            add_player(player_id)

    except ValueError:
        print(f" Error: Invalid data received from {addr}: {data}")
        server_socket.sendto("00".encode(), addr)
    except Exception as ex:
        print(f" Error handling request from {addr}: {str(ex)}")
        server_socket.sendto("00".encode(), addr)

def udp_server(ip, port):
    """
    מפעיל שרת UDP שמאזין לבקשות ומעביר אותן בהתאם למיקום מה-Database.
    """
    global server_socket  # הפיכת server_socket למשתנה גלובלי כדי שיהיה נגיש ב-request_handler
    print(" Starting UDP forwarder server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))
    print(f" Server started at {ip}:{port}, waiting for data...")

    while True:
        try:
            data, addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            print(f" Received data from {addr}")
            request_handler(data, addr)
        except Exception as ex:
            print(f" Client exception: {str(ex)}")

def main():
    udp_server(DNS_SERVER_IP, DNS_SERVER_PORT)

if __name__ == '__main__':
    main()