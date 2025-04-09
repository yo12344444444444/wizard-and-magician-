import pygame
import sys
import socket
import json
import buttons
from genericFunction import MathUtils

INVENTORY_ICON = "graphic\Inventory_Icon.png"
EXIT_ICON = "graphic\Exit_Icon.png"
CHAT_ICON = "graphic\Chat_Icon.png"
MINI_MAP_ICON = "graphic\Map_Icon.png"
NOT_OPEN_INVENTORY = r"graphic\Not_Open_Inventory.png"
FULL_INVENTORY = r"graphic\Full_Inventory.png"
FULL_HP_BAR = "graphic\Hp_Bar.png"
CHAT_WINDOW_LAYER_1 = "graphic\Chat_First_Layer.png"
CHAT_WINDOW_LAYER_2 = "graphic\Chat_Second_Layer.png"

INVENTORY_OPEN = 0 #BOOLEAN OF NUMBERS- odd=full_inventory, even=not full inventory
CHAT_OPEN = 0 #BOOLEAN OF NUMBERS- odd=open, even=close
tolernsStoneSword = 100
HOST = '127.0.0.1'
PORT = 8822
DEFAULT_BUFFER_SIZE = 1024
x, y, rect_width, rect_height = 200, 150, 48, 93
a = False

# Initialize pygame
pygame.init()

# Configurations
frames_per_second = 30
window_height = 720
window_width = 1280

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 0)
BACK = (182,212,137)

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
    # Generate the binary packet properly, ensuring it's just binary (no - or other symbols)
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
            client_socket.close()  # Close socket *after* all attempts

def open_chat():
    """
    opens the chat window
    """
    open_chat_first_layer_image = pygame.image.load(CHAT_WINDOW_LAYER_1).convert_alpha()
    open_chat_first_layer_image.set_colorkey(WHITE)
    open_chat_first_layer_image.set_alpha(180)
    chat_first_layer = buttons.Button(810, 30, open_chat_first_layer_image)
    chat_first_layer.draw(display)

    open_chat_second_layer_image = pygame.image.load(CHAT_WINDOW_LAYER_2).convert()
    open_chat_second_layer_image.set_colorkey(WHITE)
    chat_second_layer = buttons.Button(810, 30, open_chat_second_layer_image)
    chat_second_layer.draw(display)


def open_full_inventory():
    """
    draw full inventory open - items
    """
    open_full_inventory_image = pygame.image.load(FULL_INVENTORY).convert()
    open_full_inventory_image.set_colorkey(WHITE)
    full_inventory = buttons.Button(300, 119, open_full_inventory_image)
    full_inventory.draw(display)

    hp_bar_image = pygame.image.load(FULL_HP_BAR).convert()
    hp_bar_image.set_colorkey(WHITE)
    hp_bar_icon = buttons.Button(590, 170, hp_bar_image)
    hp_bar_icon.draw(display)

    conn = sqlite3.connect("DATABASE_GAME.db", check_same_thread=False)
    cursor = conn.cursor()
    print(" Successfully connected to the database.")


def open_not_full_inventory():
    """
    draw not full inventory
    """
    inventory_not_open_image = pygame.image.load(NOT_OPEN_INVENTORY).convert()
    inventory_not_open_image.set_colorkey(WHITE)
    inventory_not_open = buttons.Button(300, 570, inventory_not_open_image)
    inventory_not_open.draw(display)

    font = pygame.font.Font(None, 30)
    # hp bar:
    hp_bar_image = pygame.image.load(FULL_HP_BAR).convert()
    hp_bar_image.set_colorkey(WHITE)
    hp_bar_icon = buttons.Button(300, 520, hp_bar_image)
    hp_bar_icon.draw(display)


def create_icons():
    # inventory icon:
    inventory_image = pygame.image.load(INVENTORY_ICON).convert()
    inventory_image.set_colorkey(WHITE)
    inventory_icon = buttons.Button(370, 30, inventory_image)

    # mini map frame:
    mini_map_image = pygame.image.load(MINI_MAP_ICON).convert()
    mini_map_image.set_colorkey(WHITE)
    mini_map_icon = buttons.Button(30, 10, mini_map_image)

    # exit icon:
    exit_image = pygame.image.load(EXIT_ICON).convert()
    exit_image.set_colorkey(WHITE)
    exit_icon = buttons.Button(270, 30, exit_image)

    # chat icon:
    chat_image = pygame.image.load(CHAT_ICON).convert()
    chat_image.set_colorkey(WHITE)
    chat_icon = buttons.Button(470, 30, chat_image)

    return inventory_icon,mini_map_icon,exit_icon,chat_icon


def put_icons_on_screen(display,inventory_icon, mini_map_icon, exit_icon, chat_icon):
    """
    prints on the screen the icons, the mini map frame
    """
    global INVENTORY_OPEN
    global CHAT_OPEN

    if inventory_icon.draw(display):
        INVENTORY_OPEN += 1
    if INVENTORY_OPEN % 2 == 1:
        open_full_inventory()
    if INVENTORY_OPEN % 2 == 0:
        open_not_full_inventory()
    if exit_icon.draw(display):
        return False
    if chat_icon.draw(display):
        CHAT_OPEN += 1
    if CHAT_OPEN % 2 == 1:
        open_chat()
    mini_map_icon.draw(display)

    return True

# Main game loop
running = True
camera_x, camera_y = 0, 0  # Camera position
inventory_icon, mini_map_icon, exit_icon, chat_icon = create_icons()

while running:
    clock.tick(frames_per_second)
    display.fill(BACK)
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
            ObjectPlacer((obj_x - players_pos[1][0]+ camera_x, obj_y - players_pos[1][1]+ camera_y), obj_data[1])  # Offset by camera

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
    if not put_icons_on_screen(display, inventory_icon, mini_map_icon, exit_icon, chat_icon):
        running = False
    pygame.display.flip()

pygame.quit()
sys.exit()