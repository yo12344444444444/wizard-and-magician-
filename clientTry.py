import socket
import pickle

HOST = '127.0.0.1'
PORT = 8821
DEFAULT_BUFFER_SIZE = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
coordinates = (5, -10)  #sending coordinates
packed_coordinates = pickle.dumps(coordinates)  #make the coordinates binary form
client_socket.sendto(packed_coordinates, (HOST, PORT))
print(f"Sent coordinates to server: {coordinates}")
response, _ = client_socket.recvfrom(DEFAULT_BUFFER_SIZE)

received_data = pickle.loads(response)
print(f"Received response from secondary server: {received_data}")

client_socket.close()
