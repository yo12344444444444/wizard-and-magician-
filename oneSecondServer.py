import socket
import json
from MathUtils import MathUtils
# Server connection settings
HOST = '127.0.0.1'
PORT = 8821
DEFAULT_BUFFER_SIZE = 1024



def handle_client(packed_data, server_socket, client_addr):
    # Load existing player data from the JSON file
    try:
        with open("ips.json", "r") as f:
            y = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        y = {"players": {}}

    if "players" not in y:
        y["players"] = {}

    # Parse the incoming data
    player_data = MathUtils.parse_binary_response(packed_data)
    if not player_data:
        print(f"Invalid data from {client_addr}, ignoring...")
        return

    # Assuming the first data received is initial position, handle the player data
    for obj in player_data:
        print(obj)
        obj_id = obj[4]

        # Ensure the player data exists in the dictionary
        if obj_id not in y["players"]:
            print(f"Adding new player {obj_id}")
            y["players"][obj_id] = {"pose": f"{obj[2]},{obj[3]}", "id": obj[1], "coin": 0}
        else:
            # Update position and coin value for future updates
            y["players"][obj_id]["pose"] = f"{obj[2]},{obj[3]}"
            # If coin value is greater, update the coin and id
            if obj[4] > y["players"][obj_id]["coin"]:
                y["players"][obj_id]["coin"] = obj[4]
                y["players"][obj_id]["id"] = obj[1]

    # Save updated player data to the JSON file
    with open("ips.json", "w") as f:
        json.dump(y, f, indent=1)

    # Prepare the response to send for both players
    arr_obj = []
    for obj_id, data in y["players"].items():
        x, y_pos = map(int, data["pose"].split(","))
        id = data["id"]
        arr_obj.append((False, obj_id, x, y_pos, id))

    if not arr_obj:
        print("No objects found, sending empty response.")
        return

    # Build the response packets
    response = [MathUtils.build_array_of_packets(obj) for obj in arr_obj]
    response_in_bytes = MathUtils.response_to_bytes(response)

    # Send the response to the client
    server_socket.sendto(response_in_bytes, client_addr)


# Server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

while True:
    packed_data, client_addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
    handle_client(packed_data, server_socket, client_addr)
