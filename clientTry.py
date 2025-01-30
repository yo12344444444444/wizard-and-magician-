import socket

HOST = '10.12.9.66'  # Localhost IP address
PORT = '8821'  # Port number to connect to
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.connect((HOST, int(PORT)))

client_socket.send("Hello world!".encode('utf-8'))
print(client_socket.recv(1024))
client_socket.close()
