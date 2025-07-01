import socket
import datetime
import json

connected_clients = {}
def PortDefinder(port):
    port = port
    result = 0
    while result == 0:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('localhost', port))
        if result == 0:
            port += 1
    return port
def handle_connection(client_address, data):
    client_name = data.get('client_name', f"User_{client_address[0]}:{client_address[1]}")
    # Store client info in the dictionary
    client_port = data.get('client_port',client_address[1])
    connected_clients[client_address[0]] = {
        'name': client_name,
        'port': client_port,
        'last_seen': datetime.datetime.now()
    }

    return {
        "type": "connection_ack",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": f"Connected successfully from {client_address[0]}:{client_address[1]}",
        "client_name": client_name,
        "active_clients": len(connected_clients)
    }

def handle_chat(client_address, data, server_socket):
    # Update last seen timestamp for the client
    if client_address[0] in connected_clients:
        connected_clients[client_address[0]]['last_seen'] = datetime.datetime.now()
        sender_name = connected_clients[client_address[0]]['name']
    else:
        sender_name = 'Unknown'

    # Prepare broadcast message
    broadcast_message = {
        "type": "chat",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": data.get('content', ''),
        "client_name": sender_name
    }

    # Broadcast to all connected clients except sender
    for addr ,client in connected_clients.items():
        if addr != client_address[0]:  # Don't send back to sender
            server_socket.sendto(json.dumps(broadcast_message).encode('utf-8'), addr,client['port'])
    return broadcast_message
"""
    # Return acknowledgment to sender
    return {
        "type": "message_ack",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": f"Message broadcast to {len(connected_clients)-1} clients",
        "from": sender_name
    }
"""
def PortDefinder(port):
    port = port
    result = 0
    while result == 0:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('localhost', port))
        if result == 0:
            port += 1
    return port
def start_chat_server(host='0.0.0.0', port =PortDefinder(4200)):
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Bind the socket to the host and port
        server_socket.bind((host, port))
        print(f"Chat server started on {host}:{port}")

        while True:
            # Clean up inactive clients (no message for 5 minutes)
            current_time = datetime.datetime.now()
            inactive_clients = [
                addr for addr, client in connected_clients.items()
                if (current_time - client['last_seen']).total_seconds() > 300
            ]
            for addr in inactive_clients:
                print(f"Client {connected_clients[addr]['name']} timed out")
                del connected_clients[addr]

            # Receive message and address from client
            print("chat server recived message")
            message, client_address = server_socket.recvfrom(1024)

            try:
                # Decode JSON message
                data = json.loads(message.decode('utf-8'))
                message_type = data.get('type', '')
                message_content = data.get('content', '')
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Handle different message types
                if message_type == 'connect':
                    response = handle_connection(client_address, data)
                    print(f"[{timestamp}] New connection from {client_address[0]}:{client_address[1]}")

                elif message_type == 'chat':
                    print("recived a chat type message")
                    response = handle_chat(client_address, data, server_socket)
                    print(f"[{timestamp}] {client_address[0]}:{client_address[1]} - {data.get('message', '')}")

                else:
                    response = {
                        "type": "error",
                        "timestamp": timestamp,
                        "message": "Unknown message type"
                    }
                    print(f"[{timestamp}] Unknown message type from {client_address[0]}:{client_address[1]}")

                # Send response back to client
                print("sending message to client")
                server_socket.sendto(json.dumps(response).encode('utf-8'), client_address)

            except json.JSONDecodeError:
                error_response = {
                    "type": "error",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message": "Invalid JSON format"
                }
                server_socket.sendto(json.dumps(error_response).encode('utf-8'), client_address)

    except KeyboardInterrupt:
        print("\nShutting down the server...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_chat_server()
