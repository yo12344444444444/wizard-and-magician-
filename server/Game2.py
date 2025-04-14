from pickle import GLOBAL
import pygame
import sys
import socket
import json
from genericFunction import MathUtils
from server import clientTest

def main(token):
    global Token
    Token = token

    tolernsStoneSword = 10
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
        packet += f'{arr_obj[3]:017b}'.zfill(11)
        packet += f'{arr_obj[4]:010b}'.zfill(10)
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
        return y["On map objects"].get(id, {}).get('file', "Walking_Front_1.jpg")

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

    # כאן אנחנו משתמשים ב-Token אחרי שהוא כבר הוגדר
    game_objects = get_data()

    arr = (
        [{'category': 'player', **p} for p in game_objects['players']] +
        [{'category': 'bot', **b} for b in game_objects['bots']] +
        [{'category': 'object', **o} for o in game_objects['objects']]
    )

    # תוכל להמשיך מפה - למשל להציג אובייקטים:
    for obj in arr:
        if obj['category'] == 'object':
            ObjectPlacer((obj['x'], obj['y']), obj['id'])

def get_data():
    return clientTest.get_game_state(Token, 1920, 1080)

# קריאה ל-main עם טוקן
# לדוגמה:
# main("your_jwt_token_here")
