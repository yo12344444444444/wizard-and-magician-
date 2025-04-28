import pygame
import sys
import requests
import json
from genericFunction import MathUtils

SERVER_URL = "http://127.0.0.1:5000"


def main(ip):
    tolernsStoneSword = 10
    health = 100
    x, y, rect_width, rect_height = 200, 150, 48, 93
    a = False
    pygame.init()
    frames_per_second = 30
    window_height = 800
    window_width = 1000
    WHITE = (0, 255, 0)
    display = pygame.display.set_mode((window_width, window_height))
    clock = pygame.time.Clock()
    display.fill(WHITE)
    initial_coin = 0
    players_pos = ["n", [22222, 222222]]

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

    def get_data():
        try:
            payload = {
                "direction": players_pos[0],
                "x": players_pos[1][0],
                "y": players_pos[1][1],
                "screen_width": window_width,
                "screen_height": window_height
            }
            response = requests.post(f"{SERVER_URL}/game_state", json=payload)
            if response.status_code == 200:
                objects = response.json().get("objects", [])
                return [(True, obj['id'], obj['x'], obj['y']) for obj in objects]
            else:
                print("Failed to get game state:", response.status_code, response.text)
                return []
        except Exception as e:
            print("Error calling Flask server:", e)
            return []

    running = True
    camera_x, camera_y = 0, 0

    while running:
        clock.tick(frames_per_second)
        display.fill(WHITE)
        can_move_up = True
        can_move_down = True
        can_move_left = True
        can_move_right = True

        game_objects = get_data()
        MathUtils.setObjects(game_objects)

        ObjectPlacer((camera_x, camera_y), players_pos[0])

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
                ObjectPlacer((obj_x - players_pos[1][0] + camera_x, obj_y - players_pos[1][1] + camera_y), obj_data[1])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for obj in arr:
                    obj_x, obj_y = obj[2], obj[3]
                    screen_x = obj_x - players_pos[1][0] + camera_x
                    screen_y = obj_y - players_pos[1][1] + camera_y
                    if (
                        screen_x - tolernsStoneSword <= x <= screen_x + 48 + tolernsStoneSword and
                        screen_y - tolernsStoneSword <= y <= screen_y + 0 + tolernsStoneSword
                    ):
                        MathUtils.killObj(obj[1])
                        break

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
