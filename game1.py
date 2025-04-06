import pygame
import sys
import socket
import json
from genericFunction import MathUtils

tolernsStoneSword = 15
HOST = '127.0.0.1'
PORT = 8822
DEFAULT_BUFFER_SIZE = 1024
x, y, rect_width, rect_height = 200, 150, 48, 93
a = False

# Initialize pygame
pygame.init()

# Configurations
frames_per_second = 30
window_height = 800
window_width = 1000

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 0)

# Creating window
display = pygame.display.set_mode((window_width, window_height))
clock = pygame.time.Clock()
display.fill(WHITE)
initial_coin = 0

# Get player coin value
while True:
    try:
        initial_coin = int(input("Enter your starting coin value (0-1023): "))
        if 0 <= initial_coin <= 1023:
            break
        print("Invalid input! Please enter a number between 0 and 1023.")
    except ValueError:
        print("Invalid input! Please enter a valid number.")

# Player data
players_pos = ["n", [22222, 222222]]  # Store player positions
player_width, player_height = 48, 93


def build_array_of_packets(arr_obj):
    # Generate the binary packet properly, ensuring it's just binary (no `-` or other symbols)
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
    # Combine the array of binary strings into one large string
    combined_bit_string = ''.join(array_for_client)

    # Remove any non-binary characters (e.g., '-')
    combined_bit_string = ''.join(filter(lambda x: x in '01', combined_bit_string))

    # Ensure the length of the string is a multiple of 8, otherwise, pad with zeros
    combined_bit_string = combined_bit_string.ljust((len(combined_bit_string) + 7) // 8 * 8, '0')

    # Convert the cleaned binary string to a number and then to bytes
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


def get_data():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    retries = 3
    response_a = MathUtils.build_array_of_packets(
        (False, players_pos[0], players_pos[1][0], players_pos[1][1], initial_coin))
    response_in_bytes = response_to_bytes([response_a])

    for attempt in range(retries):
        try:
            client_socket.sendto(response_in_bytes, (HOST, PORT))
            response, _ = client_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            decoded_objects = MathUtils.parse_binary_response(response)
            return decoded_objects
        except ConnectionResetError as e:
            print(f"Connection reset on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                print("Retrying...")
            else:
                print("Max retries reached. Returning empty list.")
                return []
        finally:
            client_socket.close()  # Close socket **after** all attempts


# Main game loop
running = True
camera_x, camera_y = 0, 0  # Camera position

while running:
    clock.tick(frames_per_second)
    display.fill(WHITE)

    game_objects = get_data()
    ObjectPlacer((camera_x, camera_y), players_pos[0])
    # Adjust object positions based on camera offset
    arr = MathUtils.getObjects()
    for obj_data in arr:
        ObjectPlacer((obj_data[2] - players_pos[1][0], obj_data[3] - players_pos[1][1]),
                     obj_data[1])  # Offset by camera

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            arr = MathUtils.getObjects()
            x, y = event.pos  # Get mouse position
            for obj in arr:
                obj_x, obj_y = obj[2], obj[3]
                if obj_x - players_pos[1][0] - tolernsStoneSword <= x <= obj_x - players_pos[1][
                    0] + 93 + tolernsStoneSword and \
                        obj_y - players_pos[1][1] - tolernsStoneSword <= y <= obj_y - players_pos[1][
                    1] + 48 + tolernsStoneSword:
                    a = True
                    b = obj[1]
                    break  # Exit loop early if found
            else:
                a = False  # If no object is clicked, reset `a`

            if a:
                MathUtils.killObj(b)

    # Handle movement (keys are checked inside the event loop now)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        players_pos[1][1] -= 5
        players_pos[0] = "r"
    if keys[pygame.K_s]:
        players_pos[1][1] += 5
        players_pos[0] = "o"
    if keys[pygame.K_a]:
        players_pos[1][0] -= 5
        players_pos[0] = "p"
    if keys[pygame.K_d]:
        players_pos[1][0] += 5
        players_pos[0] = "q"

    # Keep the camera centered on the player
    camera_x = window_width // 2 - 120
    camera_y = window_height // 2 - 80

    pygame.display.flip()

pygame.quit()
sys.exit()
