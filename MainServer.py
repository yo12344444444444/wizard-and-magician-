import socket
import pickle

DNS_SERVER_IP = '0.0.0.0'
DNS_SERVER_PORT = 8821
DEFAULT_BUFFER_SIZE = 1024

FORWARDING_SERVER_IP = '127.0.0.1'
FORWARDING_SERVER_PORT = 8823

FORWARDING2_SERVER_IP = '127.0.0.1'
FORWARDING2_SERVER_PORT = 8824

FORWARDING3_SERVER_IP = '127.0.0.1'
FORWARDING3_SERVER_PORT = 8825

FORWARDING4_SERVER_IP = '127.0.0.1'
FORWARDING4_SERVER_PORT = 8826

def is_in_quadrant_one(coordinates):
    """
    Function to check if the coordinates are in the first quadrant.
    """
    x, y = coordinates
    return x > 0 and y > 0

def is_in_quadrant_second(coordinates):
    """
    Function to check if the coordinates are in the first quadrant.
    """
    x, y = coordinates
    return x < 0 and y > 0
def is_in_quadrant_3(coordinates):
    """
    Function to check if the coordinates are in the first quadrant.
    """
    x, y = coordinates
    return x < 0 and y < 0

def is_in_quadrant_4(coordinates):
    """
    Function to check if the coordinates are in the first quadrant.
    """
    x, y = coordinates
    return x > 0 and y < 0

def request_handler(data, addr):
    """
    Receives the packet from the client and forwards it to the secondary server
    only if the coordinates are in quadrant 1.
    """
    print(f"Received request from {addr}")

    try:
        # Unpack the data received from the client (now we expect a tuple)
        coordinates = pickle.loads(data)  # Expecting coordinates to be a tuple, e.g., (5, 10)
        print(f"Coordinates received: {coordinates}")

        # Check if the coordinates are in quadrant one
        if is_in_quadrant_one(coordinates):
            forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            packed_data = pickle.dumps((data, addr))  # Wrap the data with the client address
            print(f"Forwarding request to {FORWARDING_SERVER_IP}:{FORWARDING_SERVER_PORT}")
            forward_socket.sendto(packed_data, (FORWARDING_SERVER_IP, FORWARDING_SERVER_PORT))
            forward_socket.close()
        elif is_in_quadrant_second(coordinates):
            forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            packed_data = pickle.dumps((data, addr))  # Wrap the data with the client address
            print(f"Forwarding request to {FORWARDING2_SERVER_IP}:{FORWARDING2_SERVER_PORT}")
            forward_socket.sendto(packed_data, (FORWARDING2_SERVER_IP, FORWARDING2_SERVER_PORT))
            forward_socket.close()
        elif is_in_quadrant_3(coordinates):
            forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            packed_data = pickle.dumps((data, addr))  # Wrap the data with the client address
            print(f"Forwarding request to {FORWARDING3_SERVER_IP}:{FORWARDING3_SERVER_PORT}")
            forward_socket.sendto(packed_data, (FORWARDING3_SERVER_IP, FORWARDING3_SERVER_PORT))
            forward_socket.close()
        elif is_in_quadrant_4(coordinates):
            forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            packed_data = pickle.dumps((data, addr))  # Wrap the data with the client address
            print(f"Forwarding request to {FORWARDING4_SERVER_IP}:{FORWARDING4_SERVER_PORT}")
            forward_socket.sendto(packed_data, (FORWARDING4_SERVER_IP, FORWARDING4_SERVER_PORT))
            forward_socket.close()
        else:
            print(f"Coordinates {coordinates} are not in quadrant 1 or 2or 3 or 4, not forwarding request.")

    except Exception as ex:
        print(f"Error forwarding request: {str(ex)}")

def udp_server(ip, port):
    """
    Start the UDP server that listens for client requests and forwards them if valid.
    """
    print("Starting UDP forwarder server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))
    print(f"Server started at {ip}:{port} and waiting for data...")

    while True:
        try:
            data, addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            print(f"Received data from {addr}")
            request_handler(data, addr)

        except Exception as ex:
            print(f"Client exception: {str(ex)}")

def main():
    udp_server(DNS_SERVER_IP, DNS_SERVER_PORT)

if __name__ == '__main__':
    main()
