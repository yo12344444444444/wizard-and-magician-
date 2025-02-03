import socket
import pickle

DNS_SERVER_IP = '0.0.0.0'
DNS_SERVER_PORT = 8821
DEFAULT_BUFFER_SIZE = 1024

FORWARDING_SERVER_IP = '10.12.8.76'
FORWARDING_SERVER_PORT = 8823

def request_handler(data, addr):
    """
    מקבל פאקטה מהלקוח ושולח אותה לשרת המשני יחד עם כתובת הלקוח
    """
    print(f"Received request from {addr}")
    try:
        forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        packed_data = pickle.dumps((data, addr))
        forward_socket.sendto(packed_data, (FORWARDING_SERVER_IP, FORWARDING_SERVER_PORT))

        forward_socket.close()
        print(f"Forwarded request to {FORWARDING_SERVER_IP}:{FORWARDING_SERVER_PORT}")

    except Exception as ex:
        print(f"Error forwarding request: {str(ex)}")

def udp_server(ip, port):
    """
    מאזין לבקשות לקוח ומעביר אותן לשרת המשני.
    """
    print(" Starting UDP forwarder server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((ip, port))
    print(f" Server started at {ip}:{port} and waiting for data...")

    while True:
        try:
            data, addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            print(f" Received data from {addr}")
            request_handler(data, addr)

        except Exception as ex:
            print(f" Client exception: {str(ex)}")

def main():
    udp_server(DNS_SERVER_IP, DNS_SERVER_PORT)

if __name__ == '__main__':
    main()
