# server.py
import socket

PORT = 8820
BUFFER_SIZE = 1024

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("", PORT))  # Listen on all IPs

print("Server is listening...")

while True:
    data, addr = server_socket.recvfrom(BUFFER_SIZE)
    print(f"Received from {addr}: {data.decode()}")

    if data.decode().lower() == "hello":
        server_socket.sendto(b"hi", addr)
