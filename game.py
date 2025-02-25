import pygame
import sys
import socket
import json

# Server connection settings
HOST = '127.0.0.1'
PORT = 8888
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
def build_array_of_packets(arr_obj):
    """
    arr_obj[(rot,id,x,y,pos),...]
    get array with the objects and their coordinates
    build array with the small packets for the client

    protocol:
    (length of every packet-32 bits)
    bit 0: 1 for rotation, 0 for no rotation
    bits 1-7: type of the object(based on the json)
    bits 8-18: x coordinate
    bits 19-29: y coordinate
    bits 30-31: which rotation, 00 for no rotation
    """
    array_for_client = []
    if arr_obj[0]:
        packet = f'{1:01b}'
    else:
        packet = f'{0:01b}'

        # the id
    packet += f'{ord(arr_obj[1]):07b}'.zfill(7)

        # the x coordination
    packet += f'{arr_obj[2]:011b}'.zfill(11)

    # the y coordination
    packet += f'{arr_obj[3]:011b}'.zfill(11)


    if packet[0:1]== '1':
        packet += f'{arr_obj[4]:02b}'.zfill(2)
    else:
        packet += '00'

    return packet
# Initial player position
pose = [222, 2]  # Player-controlled object position (mutable list)

# Movement speed
speed = 5


def put(id):
    """Load image based on object ID from JSON file."""
    print(id)
    with open("Objects.json", "r") as f:
        y = json.load(f)
    return y["On map objects"][id]['file']


class ObjectPlacer:
    """Handles object placement in the game window."""
    def __init__(self, pos, id):
        self.pos = pos
        self.img = pygame.image.load("graphic/" + put(id))
        display.blit(self.img, pos)

def response_to_bytes(array_for_client):
    """
    gets the array of the small packets(of the protocol)
    and convert it to bytes(every small packet with 32 bits --> 4 bytes)
    """
    combined_bit_string = ''.join(array_for_client)
    number = int(combined_bit_string, 2)
    byte_value = number.to_bytes((len(combined_bit_string) + 7) // 8, 'big')
   # print(byte_value)
    return byte_value
def get_data():
    """Fetch data from the UDP server and parse it."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    response = build_array_of_packets((False, "a", pose[0],pose[1]))
    print((False, "a", pose[0],pose[1]))
    response_in_bytes = response_to_bytes(response)
    client_socket.sendto(response_in_bytes, (HOST, PORT))

    response, _ = client_socket.recvfrom(DEFAULT_BUFFER_SIZE)
    decoded_objects = parse_binary_response(response)

    client_socket.close()
    return decoded_objects


def parse_binary_response(binary_data):
    """Parse binary response into human-readable object data."""
    bit_string = ''.join(f"{byte:08b}" for byte in binary_data)
    objects = []

    # Each packet is 32 bits (4 bytes)
    for i in range(0, len(bit_string), 32):
        packet = bit_string[i:i+32]
        if len(packet) < 32:
            continue  # Ignore incomplete packets

        rotation = int(packet[0], 2)
        object_id = chr(int(packet[1:8], 2))
        x_coord = int(packet[8:19], 2)
        y_coord = int(packet[19:30], 2)
        rotation_type = int(packet[30:32], 2) if rotation else 0

        objects.append((bool(rotation), object_id, x_coord, y_coord, rotation_type))

    return objects


# Main game loop
while True:
    clock.tick(frames_per_second)

    display.fill(WHITE)  # Clear the screen **before** drawing anything

    # Fetch and display objects from the server
    game_objects = get_data()
    for obj_data in game_objects:
        print(obj_data)
        ObjectPlacer((obj_data[2], obj_data[3]), obj_data[1])  # Draw all server objects

    # Draw player-controlled object
  #  ObjectPlacer(tuple(pose), "a")  # Player always visible

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Get pressed keys for movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:  # Move up
        pose[1] -= speed
    if keys[pygame.K_s]:  # Move down
        pose[1] += speed
    if keys[pygame.K_a]:  # Move left
        pose[0] -= speed
    if keys[pygame.K_d]:  # Move right
        pose[0] += speed

    pygame.display.flip()  # Re
