import socket

HOST = '127.0.0.1'
PORT = 8826
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.sendto(response_in_bytes, (HOST, PORT))
response, _ = client_socket.recvfrom(DEFAULT_BUFFER_SIZE)
