import socket
import time

def main():
    BROADCAST_IP = "255.255.255.255"
    BUFFER_SIZE = 1024
    MESSAGE = "hello"
    PORT_RANGE = range(5000, 9000)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.settimeout(0.6)

    for port in PORT_RANGE:
        try:
            client_socket.sendto(MESSAGE.encode(), (BROADCAST_IP, port))
        except Exception as e:
            print(f"Error sending to port {port}: {e}")

    # Wait for replies
    start = time.time()
    while time.time() - start < 1:
        try:
            data, addr = client_socket.recvfrom(BUFFER_SIZE)
            return addr, data
        except socket.timeout:
            break

    client_socket.close()
