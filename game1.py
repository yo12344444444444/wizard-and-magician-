import pygame
import sys
import socket
import json
from genericFunction import MathUtils

tolernsStoneSword = 10
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
initial_coin=0
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
players_pos = ["n", [222, 2]]  # Store player positions

def build_array_of_packets(arr_obj):
    packet = f'{1:01b}' if arr_obj[0] else f'{0:01b}'
    packet += f'{ord(arr_obj[1]):07b}'.zfill(7)
    packet += f'{arr_obj[2]:011b}'.zfill(11)
    packet += f'{arr_obj[3]:011b}'.zfill(11)
    packet += f'{arr_obj[4]:010b}'.zfill(10)
    return packet

def response_to_bytes(array_for_client):
    combined_bit_string = ''.join(array_for_client)
    number = int(combined_bit_string, 2)
    byte_value = number.to_bytes((len(combined_bit_string) + 7) // 8, 'big')
    return byte_value

def put(id):
    with open("Objects.json", "r") as f:
        y = json.load(f)
    return y["On map objects"].get(id, {}).get('file', "default.png")  # Default fallback

class ObjectPlacer:
    def __init__(self, pos, id):
        self.pos = pos
        self.img = pygame.image.load(f"graphic/{put(id)}")
        display.blit(self.img, pos)

def parse_binary_response(binary_data):
    bit_string = ''.join(f"{byte:08b}" for byte in binary_data)
    objects = []
    for i in range(0, len(bit_string), 40):
        packet = bit_string[i:i+40]
        if len(packet) < 40:
            continue
        rotation = int(packet[0], 2)
        object_id = chr(int(packet[1:8], 2))
        x_coord = int(packet[8:19], 2)
        y_coord = int(packet[19:30], 2)
        objects.append((bool(rotation), object_id, x_coord, y_coord))
    return objects

def get_data():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    retries = 3
    response_a = build_array_of_packets((False, players_pos[0], players_pos[1][0], players_pos[1][1], initial_coin))
    response_in_bytes = response_to_bytes([response_a])

    for attempt in range(retries):
        try:
            client_socket.sendto(response_in_bytes, (HOST, PORT))
            response, _ = client_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            decoded_objects = parse_binary_response(response)
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
while running:
    clock.tick(frames_per_second)
    display.fill(WHITE)

    game_objects = get_data()
    for obj_data in game_objects:
        ObjectPlacer((obj_data[2], obj_data[3]), obj_data[1])  # Draw objects

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            arr = MathUtils.getObjects()
            x, y = event.pos  # Get mouse position
            for obj in arr:
                obj_x, obj_y = obj[2], obj[3]
                if obj_x - tolernsStoneSword <= x <= obj_x + 93 + tolernsStoneSword and \
                   obj_y - tolernsStoneSword <= y <= obj_y + 48 + tolernsStoneSword:
                    a = True
                    b = obj[1]
                    break  # Exit loop early if found
            else:
                a = False  # If no object is clicked, reset `a`

            if a:
                MathUtils.killObj(b)
                print("hi")

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

    pygame.display.flip()

pygame.quit()
sys.exit()
