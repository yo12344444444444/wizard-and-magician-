import pygame
import requests
import sys
import os

from lb import findy

# כתובת השרת

# קבעת נתיב לתיקיית graphic מתוך תקייה הפרויקט הראשית
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
GRAPHIC_DIR = os.path.join(BASE_DIR, "graphic")


def login_and_get_token(username, password):
    data = {"username": username, "password": password}
    response = requests.post(f"{SERVER_URL}/login", json=data)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        print("Login failed:", response.status_code, response.text)
        return None


def get_player_data(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{SERVER_URL}/player", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to get player data:", response.status_code, response.text)
        return None


def show_player_on_screen(player_data, speed=5, frame_duration=10):
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Player Viewer")
    clock = pygame.time.Clock()

    world_width, world_height = 1600, 1200
    bg_color = (144, 238, 144)  # Light green

    player_world_x = player_data.get('position_x', world_width // 2)
    player_world_y = player_data.get('position_y', world_height // 2)

    def load_images(prefix, count):
        imgs = []
        for i in range(1, count + 1):
            filename = f"{prefix}_{i}.png"
            path = os.path.join(GRAPHIC_DIR, filename)
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (50, 80))
            except Exception as e:
                print(f"Error loading {filename}:", e)
                img = pygame.Surface((50, 80), pygame.SRCALPHA)
                img.fill((255, 0, 0, 0))
            imgs.append(img)
        return imgs

    standing_img = pygame.image.load(os.path.join(GRAPHIC_DIR, 'Standing_front.png')).convert_alpha()
    standing_img = pygame.transform.scale(standing_img, (50, 80))

    walk_front = load_images('Walking_Front', 2)
    walk_left = load_images('Walking_Left', 2)
    walk_right = load_images('Walking_Right', 2)

    direction = 'front'
    frame_index = 0
    frame_counter = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_w]:
            player_world_y -= speed
            direction = 'front'
            moving = True
        elif keys[pygame.K_s]:
            player_world_y += speed
            direction = 'front'
            moving = True
        if keys[pygame.K_a]:
            player_world_x -= speed
            direction = 'left'
            moving = True
        elif keys[pygame.K_d]:
            player_world_x += speed
            direction = 'right'
            moving = True

        player_screen_x = screen_width // 2 - 25
        player_screen_y = screen_height // 2 - 40

        camera_x = player_world_x - player_screen_x
        camera_y = player_world_y - player_screen_y

        screen.fill(bg_color)

        if moving:
            frame_counter += 1
            if frame_counter >= frame_duration:
                frame_counter = 0
                frame_index = (frame_index + 1) % 2
            if direction == 'front':
                current_img = walk_front[frame_index]
            elif direction == 'left':
                current_img = walk_left[frame_index]
            else:
                current_img = walk_right[frame_index]
        else:
            current_img = standing_img
            frame_index = 0
            frame_counter = 0

        screen.blit(current_img, (player_screen_x, player_screen_y))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    data = findy.main()
    addr = data[0]
    SERVER_URL = "http://" + addr[0][0] + ":" + str(addr[0][1])
    username = input("Enter username: ")
    password = input("Enter password: ")

    token = login_and_get_token(username, password)
    if token:
        pd = get_player_data(token)
        if pd:
            show_player_on_screen(pd)
        else:
            print("Failed to retrieve player data.")
    else:
        print("Login failed. Exiting.")
