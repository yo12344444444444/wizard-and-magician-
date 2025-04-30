import socket
import time

def main():
    BROADCAST_IP = "255.255.255.255"
    BUFFER_SIZE = 1024
    MESSAGE = "hello"
    PORT_LIST = list(range(5000, 5300))
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.settimeout(0.005)

    # Send the broadcast to all known ports
    for port in PORT_LIST:
        try:
            client_socket.sendto(MESSAGE.encode(), (BROADCAST_IP, port))
            time.sleep(0.005)  # small delay to avoid flooding
        except Exception as e:
            print(f"Error sending to port {port}: {e}")

    servers = []  # List of (addr, data)
    start = time.time()

    while time.time() - start < 3:  # longer wait time
        try:
            data, addr = client_socket.recvfrom(BUFFER_SIZE)
           # print(f"Received from {addr}: {data.decode()}")
            servers.append((addr, data.decode()))
        except socket.timeout:
            break

    client_socket.close()
    return servers
if __name__ == '__main__':
    main()
