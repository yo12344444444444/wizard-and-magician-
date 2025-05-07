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
    client_socket.settimeout(5)  # Increased timeout for better chances of receiving data

    # Send the broadcast to all ports in range
    for port in PORT_LIST:
        try:
            client_socket.sendto(MESSAGE.encode(), (BROADCAST_IP, port))
            time.sleep(0.005)  # Avoid flooding
        except Exception as e:
            print(f"Error sending to port {port}: {e}")

    servers = {}  # List of (addr, response)
    start = time.time()

    while time.time() - start < 5:  # Increased timeout duration
        try:
            data, addr = client_socket.recvfrom(BUFFER_SIZE)
            print(f"Received from {addr}: {data.decode()}")  # Log what we receive
            servers[data.decode()[0:2]] = [addr[0], data.decode()[2:]]
        except socket.timeout:
            continue

    client_socket.close()
    return servers

if __name__ == '__main__':
    data = main()
    print("Received data:", data)

    # Check if 'lb' key exists in the received data before accessing it
    if 'lb' in data:
        addr = data['lb']
        print(f"Address for 'lb': {addr}")
    else:
        print("'lb' not found in the response data")
