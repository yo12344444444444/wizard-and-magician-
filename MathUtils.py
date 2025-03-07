class MathUtils:

    @staticmethod
    def build_array_of_packets(arr_obj):
        """
        Converts an array of object data into small binary packets for the client.

        Protocol:
        - Bit 0: Rotation (1 for rotation, 0 for no rotation)
        - Bits 1-7: Object type (ASCII character ID)
        - Bits 8-18: X coordinate (11 bits)
        - Bits 19-29: Y coordinate (11 bits)
        - Bits 30-31: Rotation type (2 bits)
        """
        array_for_client = []
        for obj in arr_obj:
            rotation, object_id, x_coord, y_coord, rotation_type = obj

            # Ensure object_id is a single character before converting to ASCII
            if isinstance(object_id, str) and len(object_id) == 1:
                object_id_bin = f'{ord(object_id):07b}'
            else:
                raise ValueError(f"Invalid object ID: {object_id}")

            # Construct the binary packet
            packet = f'{int(rotation):01b}'  # Bit 0: Rotation
            packet += object_id_bin  # Bits 1-7: Object ID
            packet += f'{x_coord:011b}'  # Bits 8-18: X coordinate
            packet += f'{y_coord:011b}'  # Bits 19-29: Y coordinate
            packet += f'{rotation_type:02b}' if rotation else '00'  # Bits 30-31: Rotation type

            array_for_client.append(packet)

        return array_for_client


    @staticmethod
    def response_to_bytes(array_for_client):
        """
        Converts an array of binary packets into bytes.
        """
        combined_bit_string = ''.join(array_for_client)
        number = int(combined_bit_string, 2)
        return number.to_bytes((len(combined_bit_string) + 7) // 8, 'big')



    @staticmethod
    def parse_binary_response(binary_data):
        """Parses the binary response into human-readable object data."""
        bit_string = ''.join(f"{byte:08b}" for byte in binary_data)
        objects = []

        # Each packet is 32 bits (4 bytes)
        for i in range(0, len(bit_string), 32):
            packet = bit_string[i:i + 32]
            if len(packet) < 32:
                continue  # Ignore incomplete packets

            rotation = int(packet[0], 2)
            object_id = chr(int(packet[1:8], 2))
            x_coord = int(packet[8:19], 2)
            y_coord = int(packet[19:30], 2)
            rotation_type = int(packet[30:32], 2) if rotation else 0

            objects.append((bool(rotation), object_id, x_coord, y_coord, rotation_type))

        return objects