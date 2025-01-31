import socket
import pickle  # לפענוח הנתונים

HOST = '127.0.0.1'
PORT = 8821  # שולח לשרת הראשי
DEFAULT_BUFFER_SIZE = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# שליחת הודעה לשרת הראשי
message = "Hello world!"
client_socket.sendto(message.encode('utf-8'), (HOST, PORT))
print(f"Sent message to server: {message}")

# קבלת תשובה ישירות מהשרת המשני
response, _ = client_socket.recvfrom(DEFAULT_BUFFER_SIZE)

# פענוח הקואורדינטות
coordinates = pickle.loads(response)
print(f"Received coordinates from secondary server: {coordinates}")

client_socket.close()
