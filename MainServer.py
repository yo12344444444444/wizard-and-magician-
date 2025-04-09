import socket
import pickle
import sqlite3

DNS_SERVER_IP = '0.0.0.0'
DNS_SERVER_PORT = 8826
DEFAULT_BUFFER_SIZE = 1024

FORWARDING_SERVERS = {
    1: ('127.0.0.1', 8823),  # רבעון 1
    2: ('127.0.0.1', 8824),  # רבעון 2
    3: ('127.0.0.1', 8825),  # רבעון 3
    4: ('192.168.1.79', 8826)   # רבעון 4
}

# התחברות למסד הנתונים עם טיפול בשגיאות
try:
    conn = sqlite3.connect("DATABASE_GAME.db", check_same_thread=False)
    cursor = conn.cursor()
    print("✅ Successfully connected to the database.")
except sqlite3.Error as e:
    print(f"❌ Error connecting to the database: {e}")
    exit(1)  # יציאה מהתוכנית אם לא ניתן להתחבר למסד הנתונים

def get_player_quadrant(player_id):
    """
    מחפש את השחקן במסד הנתונים לפי ה-ID ושולף את הקואורדינטות שלו כדי לקבוע את הרבעון
    """
    try:
        cursor.execute("SELECT x, y FROM players WHERE id = ?", (player_id,))
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
            print(f"⚠ Player ID {player_id} not found in database.")
            return None
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return None

def request_handler(data, addr):
    """
    מקבל פאקטה מהקליינט, מזהה את השחקן לפי ה-ID ושולח אותו לשרת המשני לפי המיקום במסד הנתונים.
    """
    print(f"📥 Received request from {addr}")

    try:
        # פירוק הנתונים שהגיעו מהקליינט - מצפים לקבל ID של שחקן
        player_id = pickle.loads(data)  # הלקוח שולח את ה-ID שלו
        print(f"🔍 Looking for player ID: {player_id}")

        quadrant = get_player_quadrant(player_id)
        if quadrant and quadrant in FORWARDING_SERVERS:
            forwarding_ip, forwarding_port = FORWARDING_SERVERS[quadrant]
            packed_data = pickle.dumps((player_id, addr))  # שולחים את ה-ID לשרת המתאים
            print(f"🚀 Forwarding request to {forwarding_ip}:{forwarding_port}")

            forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            forward_socket.sendto(packed_data, (forwarding_ip, forwarding_port))
            forward_socket.close()
        else:
            print(f"⚠ Could not determine quadrant for player ID {player_id}. Request not forwarded.")

    except Exception as ex:
        print(f"❌ Error processing request: {str(ex)}")

def udp_server(ip, port):
    """
    מפעיל שרת UDP שמאזין לבקשות ומעביר אותן בהתאם למיקום מה-Database.
    """
    print("🌐 Starting UDP forwarder server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))
    print(f"✅ Server started at {ip}:{port}, waiting for data...")

    while True:
        try:
            data, addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            print(f"📩 Received data from {addr}")
            request_handler(data, addr)

        except Exception as ex:
            print(f"❌ Client exception: {str(ex)}")

def main():
    udp_server(DNS_SERVER_IP, DNS_SERVER_PORT)

if __name__ == '__main__':
    main()
