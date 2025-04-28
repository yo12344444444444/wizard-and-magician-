import pygame
import requests
import sys
import os

SERVER_URL = "http://127.0.0.1:5000"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
GRAPHIC_DIR = os.path.join(BASE_DIR, "graphic")


def login(username, password):
    response = requests.post(f"{SERVER_URL}/login", json={"username": username, "password": password})
    if response.ok:
        return response.json().get("token")
    print("Login failed:", response.status_code, response.text)
    return None


def get_player(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{SERVER_URL}/get_player", headers=headers)
    if response.ok:
        return response.json()
    print("Failed to get player data:", response.status_code)
    return None


def get_game_state(token, direction, x, y, width, height):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"direction": direction, "x": x, "y": y, "screen_width": width, "screen_height": height}
    try:
        response = requests.post(f"{SERVER_URL}/game_state", headers=headers, json=payload)
        if response.ok:
            return response.json().get("objects", [])
        print("Failed to get game state:", response.status_code)
    except Exception as e:
        print("Error fetching game state:", e)
    return []


def load_images(prefix, count):
    images = []
    for i in range(1, count + 1):
        file = os.path.join(GRAPHIC_DIR, f"{prefix}_{i}.png")
        try:
            img = pygame.image.load(file).convert_alpha()
            img = pygame.transform.scale(img, (50, 80))
        except:
            img = pygame.Surface((50, 80), pygame.SRCALPHA)
        images.append(img)
    return images


def show_game(token, player):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Cyber Game")
    clock = pygame.time.Clock()

    bg_color = (144, 238, 144)
    player_x = player.get("position_x", 16000)
    player_y = player.get("position_y", 12000)

    standing = pygame.transform.scale(
        pygame.image.load(os.path.join(GRAPHIC_DIR, 'Standing_front.png')).convert_alpha(), (50, 80))
    walk_front = load_images('Walking_Front', 2)
    walk_left = load_images('Walking_Left', 2)
    walk_right = load_images('Walking_Right', 2)

    direction = 's'
    moving = False
    frame = 0
    frame_delay = 10
    frame_counter = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        moving = False
        if keys[pygame.K_w]: player_y -= 5; direction = 'w'; moving = True
        if keys[pygame.K_s]: player_y += 5; direction = 's'; moving = True
        if keys[pygame.K_a]: player_x -= 5; direction = 'a'; moving = True
        if keys[pygame.K_d]: player_x += 5; direction = 'd'; moving = True

        screen.fill(bg_color)
        camera_x = player_x - 400
        camera_y = player_y - 300

        objects = get_game_state(token, direction, player_x, player_y, 800, 600)
        for obj in objects:
            try:
                img = pygame.image.load(os.path.join(GRAPHIC_DIR, obj['file'])).convert_alpha()
                img = pygame.transform.scale(img, (60, 60))
                screen.blit(img, (obj['x'] - camera_x, obj['y'] - camera_y))
            except:
                continue

        if moving:
            frame_counter = (frame_counter + 1) % (frame_delay * 2)
            frame = frame_counter // frame_delay
            if direction in ['w', 's']:
                img = walk_front[frame]
            elif direction == 'a':
                img = walk_left[frame]
            else:
                img = walk_right[frame]
        else:
            img = standing

        screen.blit(img, (375, 260))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    user = input("Username: ")
    pwd = input("Password: ")
    token = login(user, pwd)
    if token:
        player = get_player(token)
        if player:
            show_game(token, player)
        else:
            print("Could not load player data.")
    else:
        print("Login failed.")
