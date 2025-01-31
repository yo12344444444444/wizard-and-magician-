import socket

DNS_SERVER_IP = '0.0.0.0'
DNS_SERVER_PORT = 8821
DEFAULT_BUFFER_SIZE = 1024

FORWARDING_SERVER_IP = '12.10.9.66'
FORWARDING_SERVER_PORT = 80

def request_handler(data, addr, server_socket):
    """
    Handles incoming requests and redirects the client to another server.
    """
    print(f"Received request from {addr}...")

    # יצירת הודעת הפניה לשרת המשני
    redirect_message = f"{FORWARDING_SERVER_IP}:{FORWARDING_SERVER_PORT}"
    print(f"Redirecting client to {redirect_message}")

    try:
        # שליחת הודעת ההפניה ללקוח
        server_socket.sendto(redirect_message.encode('utf-8'), addr)
        print(f"Redirect message sent to {addr}.")
    except Exception as ex:
        print(f"Error sending redirect message: {str(ex)}")

def udp_server(ip, port):
    """
    Main UDP server loop to receive and handle requests.
    """
    print("Starting UDP server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))
    print(f"Server started at {ip}:{port} and waiting for data...")

    while True:
        try:
            data, addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            print(f"Received data from {addr}")
            request_handler(data, addr, server_socket)
        except Exception as ex:
            print(f"Client exception: {str(ex)}")

def main():
    udp_server(DNS_SERVER_IP, DNS_SERVER_PORT)

if __name__ == '__main__':
    main()
