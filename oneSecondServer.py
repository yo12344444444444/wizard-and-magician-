import socket
import json
from genericFunction import MathUtils

# Server connection settings
HOST = '127.0.0.1'
PORT = 8821
DEFAULT_BUFFER_SIZE = 1024


def handle_client(packed_data, server_socket, client_addr):
    print(f"Received data from {client_addr}")

    # Load existing player data from JSON file
    try:
        with open("ips.json", "r") as f:
            y = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        y = {"players": {}}

    if "players" not in y:
        y["players"] = {}

    # Parse the incoming data
    player_data = MathUtils.parse_binary_response(packed_data)
    print(f"Parsed player data: {player_data}")

    if not player_data:
        print(f"Invalid data from {client_addr}, ignoring...")
        return

    updated_ids = set()  # Track updated player IDs

    # Process received player data
    for obj in player_data:
        print(f"Processing object: {obj}")

        if len(obj) < 5:
            print("Invalid object format, skipping...")
            continue

        obj_id = obj[4]  # Ensure the ID is correctly extracted
        updated_ids.add(obj_id)

        if obj_id not in y["players"]:
            print(f"Adding new player {obj_id}")
            y["players"][obj_id] = {"pose": f"{obj[2]},{obj[3]}", "id": obj[1], "coin": 0}
        else:
            y["players"][obj_id]["pose"] = f"{obj[2]},{obj[3]}"
            if obj[4] > y["players"][obj_id]["coin"]:
                y["players"][obj_id]["coin"] = obj[4]
                y["players"][obj_id]["id"] = obj[1]

    # Debugging the JSON output before writing to the file
    print("Updated player data:", json.dumps(y, indent=2))

    with open("ips.json", "w") as f:
        json.dump(y, f, indent=2)

    # Prepare the response for all players
    arr_obj = []
    for obj_id, data in y["players"].items():
        try:
            x, y_pos = map(int, data["pose"].split(","))
            id = data["id"]
            arr_obj.append((False, obj_id, x, y_pos, id))
        except ValueError as e:
            print(f"Error processing player {obj_id}: {e}")
            continue

    if not arr_obj:
        print("No objects found, sending empty response.")
        return

    # Build and send response packets
    response = [MathUtils.build_array_of_packets(obj) for obj in arr_obj]
    response_in_bytes = MathUtils.response_to_bytes(response)

    if not response_in_bytes:
        print("Response data is empty, nothing sent.")
    else:
        print(f"Sending {len(response_in_bytes)} bytes to {client_addr}")
        server_socket.sendto(response_in_bytes, client_addr)


# Server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))
print(f"Server listening on {HOST}:{PORT}")

while True:
    packed_data, client_addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
    handle_client(packed_data, server_socket, client_addr)
