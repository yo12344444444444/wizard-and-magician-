import os
import socket
from PIL import Image


IP = '0.0.0.0'
PORT = 8821  # ?
EXP = "3wallpaper.jpg"


def open_file(data):
    if os.path.exists(data):
        print("found file")
        file_data = Image.open(data)
        file_data.show()
        file_data.close()
    else:
        print("did not found file")


def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))
    print("server is listening")
    (data, client_address) = server_socket.recvfrom(1024)
    open_file(data)
    server_socket.close()


def main():
    # udp_server()
    open_file(EXP)


if __name__ == "__main__":
    main()
