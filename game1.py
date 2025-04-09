import pygame
import sys
import socket
import json
from genericFunction import MathUtils

def main(ip):
    tolernsStoneSword = 10
    HOST = ip
    PORT = 8827
    health = 100
    DEFAULT_BUFFER_SIZE = 1024
    x, y, rect_width, rect_height = 200, 150, 48, 93
    a = False
    pygame.init()
    frames_per_second = 30
    window_height = 800
    window_width = 1000
    WHITE = (0, 255, 0)
    BLUE = (0, 0, 0)
    display = pygame.display.set_mode((window_width, window_height))
    clock = pygame.time.Clock()
    display.fill(WHITE)
    initial_coin = 0
    players_pos = ["n", [22222, 222222]]


    def build_array_of_packets(arr_obj):
        packet = f'{1:01b}' if arr_obj[0] else f'{0:01b}'
        packet += f'{ord(arr_obj[1]):07b}'.zfill(7)
        packet += f'{arr_obj[2]:017b}'.zfill(11)
        #  print(packet)
        packet += f'{arr_obj[3]:017b}'.zfill(11)
        packet += f'{arr_obj[4]:010b}'.zfill(10)
        # Make sure no non-binary characters are present
        if not all(c in '01' for c in packet):
            raise ValueError(f"Invalid binary string: {packet}")

        return packet


    def response_to_bytes(array_for_client):
        combined_bit_string = ''.join(array_for_client)
        combined_bit_string = ''.join(filter(lambda x: x in '01', combined_bit_string))
        combined_bit_string = combined_bit_string.ljust((len(combined_bit_string) + 7) // 8 * 8, '0')
        number = int(combined_bit_string, 2)
        byte_value = number.to_bytes((len(combined_bit_string) + 7) // 8, 'big')

        return byte_value


    def put(id):
        with open("Objects.json", "r") as f:
            y = json.load(f)
        return y["On map objects"].get(id, {}).get('file', "Walking_Front_1.jpg")  # Default fallback


    class ObjectPlacer:
        def __init__(self, pos, id):
            self.pos = pos
            self.img = pygame.image.load(f"graphic/{put(id)}")
            self.img.set_colorkey((255, 255, 255))
            display.blit(self.img, pos)


    def parse_binary_response(binary_data):
        bit_string = ''.join(f"{byte:08b}" for byte in binary_data)
        objects = []
        for i in range(0, len(bit_string), 52):
            packet = bit_string[i:i + 52]
            if len(packet) < 52:
                continue
            rotation = int(packet[0], 2)
            object_id = chr(int(packet[1:8], 2))
            x_coord = int(packet[8:25], 2)
            y_coord = int(packet[25:42], 2)
            objects.append((bool(rotation), object_id, x_coord, y_coord))
        return objects


    def health_redcation(data):
        global health
        health -= int(data[1:8], 2)


    def get_data():
        global decoded_objects
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        retries = 3
        response_a = MathUtils.build_array_of_packets(
            (False, players_pos[0], players_pos[1][0], players_pos[1][1], initial_coin))
        response_in_bytes = response_to_bytes([response_a])

        for attempt in range(retries):
            try:
                client_socket.sendto(response_in_bytes, (HOST, PORT))
                response, _ = client_socket.recvfrom(DEFAULT_BUFFER_SIZE)
                if response[0]:
                    #           health_redcation(response)
                    pass
                decoded_objects = MathUtils.parse_binary_response(response)
                print(decoded_objects)
                # else:
                #    pass
                #  decoded_objects = MathUtils.parse_binary_response(response)
                return decoded_objects
            except ConnectionResetError as e:
                print(f"Connection reset on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    print("Retrying...")
                else:
                    print("Max retries reached. Returning empty list.")
                    return []
            finally:
                client_socket.close()  # Close socket *after* all attempts


    r = True
    while r:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(6)
        client_socket.sendto("2212".encode(), (HOST, PORT))
        response, _ = client_socket.recvfrom(DEFAULT_BUFFER_SIZE)
        print(response)
        if response is not None:
            r = False
    running = True
    camera_x, camera_y = 0, 0  # Camera position

    while running:
        clock.tick(frames_per_second)
        display.fill(WHITE)
        can_move_up = True
        can_move_down = True
        can_move_left = True
        can_move_right = True
        game_objects = get_data()
        ObjectPlacer((camera_x, camera_y), players_pos[0])
        # Adjust object positions based on camera offset
        arr = MathUtils.getObjects()
        for obj_data in arr:
            obj_x, obj_y = obj_data[2], obj_data[3]
            if int(obj_data[1]) != initial_coin:
                if obj_x - 80 <= players_pos[1][0] <= obj_x + 80 and obj_y - 122 <= players_pos[1][1] <= obj_y + 122:
                    if players_pos[1][1] > obj_y:
                        can_move_up = False
                    if players_pos[1][1] < obj_y:
                        can_move_down = False
                    if players_pos[1][0] > obj_x:
                        can_move_left = False
                    if players_pos[1][0] < obj_x:
                        can_move_right = False

            if int(obj_data[1]) != initial_coin:
                ObjectPlacer((obj_x - players_pos[1][0] + camera_x, obj_y - players_pos[1][1] + camera_y),
                             obj_data[1])  # Offset by camera

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos  # Get mouse position on screen

                for obj in arr:
                    obj_x, obj_y = obj[2], obj[3]
                    screen_x = obj_x - players_pos[1][0] + camera_x
                    screen_y = obj_y - players_pos[1][1] + camera_y

                    if (
                            screen_x - tolernsStoneSword <= x <= screen_x + 48 + tolernsStoneSword and
                            screen_y - tolernsStoneSword <= y <= screen_y + 0 + tolernsStoneSword
                    ):
                        MathUtils.killObj(obj[1])  # Kill the object by ID
                        break  # Exit loop after first kill

        # Handle movement (keys are checked inside the event loop now)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and can_move_up:
            players_pos[1][1] -= 5
            players_pos[0] = "r"
        if keys[pygame.K_s] and can_move_down:
            players_pos[1][1] += 5
            players_pos[0] = "o"
        if keys[pygame.K_a] and can_move_left:
            players_pos[1][0] -= 5
            players_pos[0] = "p"
        if keys[pygame.K_d] and can_move_right:
            players_pos[1][0] += 5
            players_pos[0] = "q"

        camera_x = window_width // 2 - 120
        camera_y = window_height // 2 - 80

        pygame.display.flip()

    pygame.quit()
    sys.exit()
