import pygame
import sys
import socket
import json

# Server connection settings
HOST = '127.0.0.1'  # Use the server's IP address here
PORT = 8821
DEFAULT_BUFFER_SIZE = 1024

# Initialize pygame
pygame.init()

# Configurations
frames_per_second = 30
window_height = 800
window_width = 1000

# Colors
WHITE = (255, 255, 255)

# Creating window
display = pygame.display.set_mode((window_width, window_height))
clock = pygame.time.Clock()
display.fill(WHITE)

# Ask for the player's initial coin value (must be between 0-1023)
while True:
    try:
        initial_coin = int(input("Enter your starting coin value (0-1023): "))
        if 0 <= initial_coin <= 1023:
            break
        print("Invalid input! Please enter a number between 0 and 1023.")
    except ValueError:
        print("Invalid input! Please enter a valid number.")

# Player data
players_pos = {"a": [222, 2]}  # Store player positions
players_coins = [0,initial_coin]  # Store player coin values

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
    return y["On map objects"][id]['file']

class ObjectPlacer:
    def __init__(self, pos, id):
        self.pos = pos
        self.img = pygame.image.load("graphic/" + put(id))
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
    coin_value_a = players_coins[1]
    response_a = build_array_of_packets((False, "a", players_pos["a"][0], players_pos["a"][1], coin_value_a))
    response_in_bytes = response_to_bytes([response_a])

    for attempt in range(retries):
        try:
            client_socket.sendto(response_in_bytes, (HOST, PORT))
            response, _ = client_socket.recvfrom(DEFAULT_BUFFER_SIZE)
            decoded_objects = parse_binary_response(response)
            # Update player coins and other data
            for obj in decoded_objects:
                print(obj)

            return decoded_objects
        except ConnectionResetError as e:
            print(f"Connection reset on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                print("Retrying...")
            else:
                print("Max retries reached. Returning empty list.")
                return []  # Return empty list if retries are exhausted
        finally:
            client_socket.close()

# Main game loop
while True:
    clock.tick(frames_per_second)
    display.fill(WHITE)

    game_objects = get_data()
    for obj_data in game_objects:
        ObjectPlacer((obj_data[2], obj_data[3]), obj_data[1])  # Draw objects

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    # Player a movement (WASD)
    if keys[pygame.K_w]:
        players_pos["a"][1] -= 5
    if keys[pygame.K_s]:
        players_pos["a"][1] += 5
    if keys[pygame.K_a]:
        players_pos["a"][0] -= 5
    if keys[pygame.K_d]:
        players_pos["a"][0] += 5

    pygame.display.flip()
