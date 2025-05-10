import socket
import time


class findy:
    def __init__(self):
        self.servers = {}

    def main(self,port):
        BROADCAST_IP = "255.255.255.255"
        BUFFER_SIZE = 1024
        MESSAGE = "r"+str(port)
        PORT_LIST = list(range(5000, 5300))

        # Use UDP socket for broadcasting
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client_socket.settimeout(5)  # Increased timeout for better chances of receiving data

        # Send the broadcast to all ports in range
        for port in PORT_LIST:
            try:
                client_socket.sendto(MESSAGE.encode(), (BROADCAST_IP, port))
                time.sleep(0.005)  # Avoid flooding
            except Exception as e:
                pass
        start = time.time()

        while time.time() - start < 1:  # Increased timeout duration
            try:
                data, addr = client_socket.recvfrom(BUFFER_SIZE)
                msg = data.decode()
                if '|' in msg:
                    prefix, port = msg.split('|')
                    print(prefix, port)
                    self.servers[prefix] = [addr[0], port]
            except socket.timeout:
                continue
        client_socket.close()
        return self.servers

    def serve(self):
        BROADCAST_IP = "255.255.255.255"
        BUFFER_SIZE = 1024
        MESSAGE = "hello"
        PORT_LIST = list(range(5000, 5300))

        # Use UDP socket for broadcasting
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        client_socket.settimeout(5)  # Increased timeout for better chances of receiving data

        # Send the broadcast to all ports in range
        for port in PORT_LIST:
            try:
                client_socket.sendto(MESSAGE.encode(), (BROADCAST_IP, port))
                time.sleep(0.005)  # Avoid flooding
            except Exception as e:
                pass
        servers = {}  # List of (addr, response)
        start = time.time()

        while time.time() - start < 5:  # Increased timeout duration
            try:
                data, addr = client_socket.recvfrom(BUFFER_SIZE)
                servers[data.decode()[0:2]] = [addr[0], data.decode()[2:]]
            except socket.timeout:
                continue

        client_socket.close()
        return servers
