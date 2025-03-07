import json
import socket
import MathUtils

IP = '127.0.0.1'
PORT = 8824
DEFAULT_BUFFER_SIZE = 1024


def handle_client(packed_data, server_socket, client_addr):
    """
    Handles incoming client requests and sends the processed object data.
    """
    with open("ips.json", "r") as f:
        y = json.load(f)

    # Ensure "plyers" key exists
    if "plyers" not in y:
        y["plyers"] = {}

    # Update client data in "plyers"
    y["plyers"][client_addr[0]] = MathUtils.MathUtils.parse_binary_response(packed_data)

    # Save updated data back to the file
    with open("ips.json", "w") as f:
        json.dump(y, f, indent=4)

    try:
        # Extract object data from "plyers"
        arr_obj = []
        for ip, data in y.get("plyers", {}).items():
            if isinstance(data, list):
                arr_obj.extend(data)  # Flatten list of objects

        # Debugging step
        print(f"Extracted Objects: {arr_obj}")

        if not arr_obj:
            print("No objects found, sending empty response.")
            return  # Do not send empty packets

        # Convert object data into binary packets
        response = MathUtils.MathUtils.build_array_of_packets(arr_obj)

        # Convert binary packets to bytes
        response_in_bytes = MathUtils.MathUtils.response_to_bytes(response)

        # Send response to client
        server_socket.sendto(response_in_bytes, client_addr)

    except Exception as ex:
        print(f"Error handling client: {str(ex)}")


def udp_server():
    """
    Listens for UDP packets from the main server and processes them.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))

    while True:
        try:
            packed_data, client_addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            handle_client(packed_data, server_socket, client_addr)
        except Exception as ex:
            print(f"Client exception: {str(ex)}")

def main():
    udp_server()

if __name__ == "__main__":
    main()
