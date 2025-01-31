import socket
import pickle  # ספרייה שממירה אובייקטים לבינארי
from PIL import Image


IP = '10.12.9.72'
PORT = 8821  # ?
DEFAULT_BUFFER_SIZE = 1024
EXP = "3wallpaper.jpg"


def handle_client(data, addr, server_socket):
    """
    send to the client tuple with coordinates
    """
    x = 0
    y = 0
    coordinates = (x, y)
    coordinates_binary = pickle.dumps(coordinates)
    server_socket.sendto(coordinates_binary, addr)


def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))
    print("server is listening")
    while True:
        try:
            (data, addr) = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            handle_client(data, addr, server_socket)
        except Exception as ex:
            print("Client exception! %s" % (str(ex)))
    # server_socket.close()


def main():
    udp_server()


if __name__ == "__main__":
    main()
