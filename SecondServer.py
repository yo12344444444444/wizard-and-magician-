import socket
import pickle

IP = '0.0.0.0'
PORT = 8820
DEFAULT_BUFFER_SIZE = 1024

def handle_client(packed_data, server_socket):
    """
    Receives a packet from the main server (including client data + client address),
    and responds directly to the client with the message "You have reached me, you're in quadrant 1."
    """
    try:
        # Unpack the data and extract the client address
        data, client_addr = pickle.loads(packed_data)
        print(f"Handling request from {client_addr}")

        # Instead of coordinates, returning a custom message
        message = "You have reached me, you're in quadrant 2"
        response = pickle.dumps(message)  # Pack the message as binary data
        server_socket.sendto(response, client_addr)
        print(f"Response '{message}' sent to {client_addr}")

    except Exception as ex:
        print(f"Error handling client: {str(ex)}")

def udp_server():
    """
    Listens for requests from the main server and sends a response directly to the client.
    """
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))
    print(f"Secondary server listening on {IP}:{PORT}")

    while True:
        try:
            # Receive a packed request from the main server
            packed_data, _ = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            handle_client(packed_data, server_socket)  # Process the request
        except Exception as ex:
            print(f"Client exception: {str(ex)}")

def main():
    udp_server()

if __name__ == "__main__":
    main()
