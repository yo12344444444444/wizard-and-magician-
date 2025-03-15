import json
class MathUtils:
    def getObjects():
        with open("ips.json", "r") as f:
             y = json.load(f)

        if "players" not in y:
            y["players"] = {}


        arr_obj = []
        for obj_id, data in y["players"].items():
            x, y_pos = map(int, data["pose"].split(","))
            id = data["id"]
            arr_obj.append((False, obj_id, x, y_pos, id))
           # print(arr_obj)
        return arr_obj

    @staticmethod
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

    @staticmethod
    def response_to_bytes(array_for_client):
        """ Converts the array of packets into bytes (each 40-bit packet → 5 bytes). """
        combined_bit_string = ''.join(array_for_client)
        number = int(combined_bit_string, 2)
        byte_value = number.to_bytes((len(combined_bit_string) + 7) // 8, 'big')
        return byte_value

    @staticmethod
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
