import socket
import time

def main():
    BROADCAST_IP = "255.255.255.255"
    BUFFER_SIZE = 1024
    MESSAGE = "r"
    PORT_LIST = list(range(5000, 5300))

    # Use UDP socket for broadcasting
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.settimeout(0.1)

    # Send the broadcast to all ports in range
    for port in PORT_LIST:
        try:
            client_socket.sendto(MESSAGE.encode(), (BROADCAST_IP, port))
            time.sleep(0.005)  # Avoid flooding
        except Exception as e:
            print(f"Error sending to port {port}: {e}")

    servers = []  # List of (addr, response)
    start = time.time()

    while time.time() - start < 3:
        try:
            data, addr = client_socket.recvfrom(BUFFER_SIZE)
            servers.append((addr, data.decode()))
        except socket.timeout:
            continue

    client_socket.close()
    return servers

if __name__ == '__main__':
    print(main())
