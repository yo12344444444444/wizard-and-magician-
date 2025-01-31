import socket
import pickle  # לטיפול בנתונים בינאריים

IP = '127.0.0.1'
PORT = 8822
DEFAULT_BUFFER_SIZE = 1024

def handle_client(packed_data, server_socket):
    """
    מקבל פאקטה מהשרת הראשי (שכוללת נתוני לקוח + כתובת הלקוח),
    מחזיר ישירות ללקוח tuple עם קואורדינטות.
    """
    try:
        data, client_addr = pickle.loads(packed_data)
        print(f"Handling request from {client_addr}")
        coordinates = (0, 0)
        response = pickle.dumps(coordinates)
        server_socket.sendto(response, client_addr)
        print(f"Response {coordinates} sent to {client_addr}")

    except Exception as ex:
        print(f"Error handling client: {str(ex)}")

def udp_server():
    """
    מאזין לבקשות מהשרת הראשי ושולח תשובה ישירות ללקוח.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))
    print(f"Secondary server listening on {IP}:{PORT}")

    while True:
        try:
            packed_data, _ = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            handle_client(packed_data, server_socket)
        except Exception as ex:
            print(f"Client exception: {str(ex)}")

def main():
    udp_server()

if __name__ == "__main__":
    main()
