import socket
import pickle

# הגדרת כתובת השרת
server_ip = '127.0.0.1'
server_port = 8822
server_address = (server_ip, server_port)

def send_position_to_server():
    """שליחה של קואורדינטות לשרת"""
    data = {
        "action": "update_position",  # פעולה לעדכון
        "username": "player1",        # שם השחקן
        "position": (5, -10)          # קואורדינטות X ו-Y
    }

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        packed_data = pickle.dumps(data)  # סדר את הנתונים לשליחה
        client_socket.sendto(packed_data, server_address)
        print("Sent coordinates to server:", data["position"])

        # המתנה לתגובה מהשרת
        response, _ = client_socket.recvfrom(1024)
        print("Received response from server:", pickle.loads(response))


def main():
    """הפונקציה הראשית"""
    send_position_to_server()


if __name__ == "__main__":
    main()
