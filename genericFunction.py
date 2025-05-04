import json
class MathUtils:
    def getObjects(self):
        with open("ips.json", "r") as f:
             y = json.load(f)

        if "players" not in y:
            y["players"] = {}


        ar_obj = []
        for obj_id, data in y["players"].items():
            x, y_pos = map(int, data["pose"].split(","))
            id = data["id"]
            arr_obj.append((False, obj_id, x, y_pos, id))
        return arr_obj
    @staticmethod
    def killObj(id):
        with open("ips.json", "r+") as f:
            data = json.load(f)  # Load JSON data

            if "players" in data and id in data["players"]:
                data["players"].pop(id)  # Remove the ID if it exists

                f.seek(0)  # Move cursor to the beginning of the file
                json.dump(data, f, indent=4)  # Write updated JSON with indentation
                f.truncate()  # Remove leftover content if file size shrinks
            else:
                print(f"ID {id} not found in players.")
    @staticmethod
    def build_array_of_packets(arr_obj):
        """
        arr_obj[(rot, id, x, y, coin),...]
        Protocol (52-bit packet):
        bit 0: 1 for rotation, 0 for no rotation
        bits 1-7: type of the object (from JSON)
        bits 8-25: x coordinate
        bits 25-42: y coordinate
        bits 42-52: coin value (10 bits)
        """
        packet = f'{0:01b}'.zfill(1)

        # Object ID (7 bits)
        packet += f'{ord(arr_obj[1]):07b}'.zfill(7)

        # X Coordinate (11 bits)
        packet += f'{arr_obj[2]:017b}'.zfill(17)

        # Y Coordinate (11 bits)
        packet += f'{arr_obj[3]:017b}'.zfill(17)

        coin_value = int(arr_obj[4])  # Ensure this is an integer (coin value, not object id)
        packet += f'{coin_value:010b}'.zfill(10)
        packet += '0000'  # <--- Add 4 bits padding

        return packet

    @staticmethod
    def response_to_bytes(array_for_client):
        """ Converts the array of packets into bytes (each 40-bit packet → 5 bytes). """
        combined_bit_string = ''.join(array_for_client)
        number = int(combined_bit_string, 2)
        byte_value = number.to_bytes((len(combined_bit_string) + 7) // 8, 'big')
        return byte_value

    @staticmethod
    def parse_binary_response(binary_data):
        bit_string = ''.join(f"{byte:08b}" for byte in binary_data)
        objects = []

        for i in range(0, len(bit_string), 56):  # 56-bit packets now
            packet = bit_string[i:i+56]
            if len(packet) < 52:
                continue  # Ignore incomplete packets
            rotation = int(packet[0], 2)
            object_id = chr(int(packet[1:8], 2))
            x_coord = int(packet[8:25], 2)
            y_coord = int(packet[25:43], 2)

            # Extract the 10-bit coin_value portion, and handle the case where it might be empty
            coin_value_str = packet[43:53]
            if coin_value_str and all(c in '01' for c in coin_value_str):  # Check if it's valid binary
                coin_value = int(coin_value_str, 2)
            else:
                coin_value = 0  # Default value if coin_value field is malformed or empty

            objects.append((bool(rotation), object_id, x_coord, y_coord, coin_value))
        return objects

