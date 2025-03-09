import socket
import json

# Server connection settings
HOST = '127.0.0.1'
PORT = 8822
DEFAULT_BUFFER_SIZE = 1024

def build_array_of_packets(arr_obj):
    """
    arr_obj[(rot, id, x, y, coin),...]
    Protocol (40-bit packet):
    bit 0: 1 for rotation, 0 for no rotation
    bits 1-7: type of the object (from JSON)
    bits 8-18: x coordinate
    bits 19-29: y coordinate
    bits 30-39: coin value (10 bits)
    """
    packet = f'{1:01b}' if arr_obj[0] else f'{0:01b}'

    # Object ID (7 bits)
    packet += f'{ord(arr_obj[4]):07b}'.zfill(7)

    # X Coordinate (11 bits)
    packet += f'{arr_obj[2]:011b}'.zfill(11)

    # Y Coordinate (11 bits)
    packet += f'{arr_obj[3]:011b}'.zfill(11)

    # Coin Value (10 bits)
    coin_value = int(arr_obj[1])  # Ensure this is an integer (coin value, not object id)
    print(coin_value)
    packet += f'{coin_value:010b}'.zfill(10)

    return packet

def response_to_bytes(array_for_client):
    """ Converts the array of packets into bytes (each 40-bit packet → 5 bytes). """
    combined_bit_string = ''.join(array_for_client)
    number = int(combined_bit_string, 2)
    byte_value = number.to_bytes((len(combined_bit_string) + 7) // 8, 'big')
    return byte_value

def parse_binary_response(binary_data):
    """ Parses the binary response into human-readable object data. """
    bit_string = ''.join(f"{byte:08b}" for byte in binary_data)
    objects = []

    for i in range(0, len(bit_string), 40):  # Now packets are 40 bits
        packet = bit_string[i:i+40]
        if len(packet) < 40:
            continue  # Ignore incomplete packets

        rotation = int(packet[0], 2)
        object_id = chr(int(packet[1:8], 2))
        x_coord = int(packet[8:19], 2)
        y_coord = int(packet[19:30], 2)
        coin_value = int(packet[30:40], 2)

        objects.append((bool(rotation), object_id, x_coord, y_coord, coin_value))

    return objects

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
    player_data = parse_binary_response(packed_data)
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
    response = [build_array_of_packets(obj) for obj in arr_obj]
    response_in_bytes = response_to_bytes(response)

    # Send the response to the client
    server_socket.sendto(response_in_bytes, client_addr)


# Server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

while True:
    packed_data, client_addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
    handle_client(packed_data, server_socket, client_addr)
