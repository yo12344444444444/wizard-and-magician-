import os
import socket
from PIL import Image


IP = '10.12.9.72'
PORT = 8821  # ?
DEFAULT_BUFFER_SIZE = 1024
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
    while True:
        try:
            (data, addr) = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            print(f"got from {addr}: {data}")
            open_file(data)
        except Exception as ex:
            print("Client exception! %s" % (str(ex)))
    # server_socket.close()


def main():
    udp_server()


if __name__ == "__main__":
    main()
