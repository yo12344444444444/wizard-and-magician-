import pygame
import requests
import sys
import time
import os

# Initialize Pygame
pygame.init()

# Constants for screen dimensions
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
FPS = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)

# Your API URL
API_URL = 'http://127.0.0.1:5000'

# Pygame screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bot Visualization')

# Font for displaying text
font = pygame.font.SysFont('Arial', 16)

# Load ghost images (bot sprites)
def load_images():
    try:
        current_dir = os.getcwd()
        parent_dir = os.path.dirname(current_dir)
        base_path = os.path.join(parent_dir, 'graphic', 'bot')
        print(f"Looking for images in: {base_path}")
        ghost_images = {
            'front': pygame.image.load(os.path.join(base_path, 'Ghost_Front.png')).convert(),
            'back': pygame.image.load(os.path.join(base_path, 'Ghost_Back.png')).convert(),
            'left': pygame.image.load(os.path.join(base_path, 'Ghost_Left.png')).convert(),
            'right': pygame.image.load(os.path.join(base_path, 'Ghost_Right.png')).convert()
        }
        for key in ghost_images:
            ghost_images[key].set_colorkey(WHITE)
        return ghost_images
    except pygame.error as e:
        print(f"Error loading bot images: {e}")
        return None

# Load player image
def load_player_image():
    try:
        current_dir = os.getcwd()
        parent_dir = os.path.dirname(current_dir)
        player_path = os.path.join(parent_dir, 'graphic', 'Standing_front.png')
        print(f"Looking for player image at: {player_path}")
        return pygame.image.load(player_path).convert_alpha()
    except pygame.error as e:
        print(f"Error loading player image: {e}")
        return None

# Draw an object relative to the player's position
def draw_object(screen, obj, player_x, player_y, object_images):
    obj_x = obj.get('x', 0)
    obj_y = obj.get('y', 0)
    file_name = obj.get('file')

    object_location_x = (obj_x - player_x) + (SCREEN_WIDTH // 2)
    object_location_y = (obj_y - player_y) + (SCREEN_HEIGHT // 2)

    if file_name and file_name.lower().endswith('.png') and file_name.lower() in object_images:
        obj_img = object_images[file_name.lower()]
        obj_rect = obj_img.get_rect(center=(object_location_x, object_location_y))
        screen.blit(obj_img, obj_rect)

# Load all object images from the graphic folder
def load_object_images():
    try:
        current_dir = os.getcwd()
        parent_dir = os.path.dirname(current_dir)
        object_path = os.path.join(parent_dir, 'graphic')
        print(f"Looking for object images in: {object_path}")
        object_images = {}

        for filename in os.listdir(object_path):
            if filename.endswith('.png'):
                name = filename.lower()
                full_path = os.path.join(object_path, filename)
                image = pygame.image.load(full_path).convert()
                image.set_colorkey((255, 255, 255))
                object_images[name] = image

        return object_images

    except pygame.error as e:
        print(f"Error loading object images: {e}")
        return {}

# Login and get token
def login(username, password):
    try:
        response = requests.post(f'{API_URL}/login', json={'username': username, 'password': password})
        if response.status_code == 200:
            token = response.json().get('token')
            print(f"Login successful! Token: {token}")
            return token
        else:
            print(f"Login error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return None

# Handle player movement and request updated game state
def handle_player_movement(token, screen_width, screen_height):
    keys = pygame.key.get_pressed()
    direction = None

    if keys[pygame.K_w]:
        direction = 'w'
    elif keys[pygame.K_a]:
        direction = 'a'
    elif keys[pygame.K_s]:
        direction = 's'
    elif keys[pygame.K_d]:
        direction = 'd'

    if direction:
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'direction': direction,
            'screen_width': screen_width,
            'screen_height': screen_height
        }
        try:
            response = requests.post(f'{API_URL}/movement', json=data, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Movement error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error sending movement: {e}")
    return None

# Get current player data
def get_player_data(token):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{API_URL}/get_player', headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching player data: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection error fetching player data: {e}")
        return None

# Get full game state
def get_game_state(token, screen_width, screen_height):
    start = time.time()
    try:
        headers = {'Authorization': f'Bearer {token}'}
        data = {'screen_width': screen_width, 'screen_height': screen_height}
        response = requests.post(f'{API_URL}/game_state', json=data, headers=headers)
        if response.status_code == 200:
            game_state_data = response.json()
            if 'bots' in game_state_data:
                print(f"[DEBUG] Received {len(game_state_data['bots'])} bots from server.")
            print(f"get_game_state client: {time.time() - start}")
            return game_state_data
        else:
            print(f"Error fetching game state: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Connection error fetching game state: {e}")
    return None

# Draw a bot relative to the player
def draw_bot(screen, bot, player_x, player_y, ghost_images):
    print(f"[DEBUG] Drawing bot: {bot}")
    bot_x = bot.get('x', 0)
    bot_y = bot.get('y', 0)
    direction = bot.get('direction', 'front').lower()

    bot_location_x = (bot_x - player_x) + (SCREEN_WIDTH // 2)
    bot_location_y = (bot_y - player_y) + (SCREEN_HEIGHT // 2)

    if direction in ('up', 'back'):
        ghost_img = ghost_images.get('back')
        print(f"[DEBUG] Bot direction: {direction}, using image: back")
    elif direction in ('down', 'front'):
        ghost_img = ghost_images.get('front')
        print(f"[DEBUG] Bot direction: {direction}, using image: front")
    elif direction == 'left':
        ghost_img = ghost_images.get('left')
        print(f"[DEBUG] Bot direction: {direction}, using image: left")
    elif direction == 'right':
        ghost_img = ghost_images.get('right')
        print(f"[DEBUG] Bot direction: {direction}, using image: right")
    else:
        ghost_img = ghost_images.get('front')
        print(f"[DEBUG] Unknown bot direction: {direction}, using image: front")

    if ghost_img:
        img_rect = ghost_img.get_rect(center=(bot_location_x, bot_location_y))
        screen.blit(ghost_img, img_rect)
    else:
        print(f"[WARNING] No image found for bot direction: {direction}")

# Draw the player in the center
def draw_player(screen, player_image):
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    player_rect = player_image.get_rect(center=(center_x, center_y))
    screen.blit(player_image, player_rect)

# Main game loop
def main():
    ghost_images = load_images()
    player_image = load_player_image()
    object_images = load_object_images()

    if not ghost_images:
        print("Error: Bot images were not loaded.")
        return
    if not player_image:
        print("Error: Player image was not loaded.")
        return
    if not object_images:
        print("Error: Object images were not loaded.")
        return

    username = '2212'
    password = '2212'
    token = login(username, password)
    if not token:
        print("Login failed. Exiting...")
        return

    clock = pygame.time.Clock()
    running = True
    while running:
        start = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        print(f"part1: {time.time() - start}")

        start = time.time()
        game_state = handle_player_movement(token, SCREEN_WIDTH, SCREEN_HEIGHT)
        print(f"part2: {time.time() - start}")

        start = time.time()
        if not game_state:
            game_state = get_game_state(token, SCREEN_WIDTH, SCREEN_HEIGHT)
        print(f"part3: {time.time() - start}")

        start = time.time()
        player_data = get_player_data(token)
        if player_data and player_data.get('health', 100) <= 0:
            print("[INFO] Player is dead. Attempting to respawn...")
            try:
                headers = {'Authorization': f'Bearer {token}'}
                respawn_response = requests.post(f'{API_URL}/respawn', headers=headers)
                if respawn_response.status_code == 200:
                    print("[INFO] Player respawned successfully.")
                    player_data = get_player_data(token)
                else:
                    print(f"[ERROR] Respawn failed: {respawn_response.status_code} - {respawn_response.text}")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Connection error while respawning: {e}")
        screen.fill(GREEN)
        print(f"part4: {time.time() - start}")

        start = time.time()
        if player_data and game_state and 'objects' in game_state:
            player_x = player_data.get('position_x', SCREEN_WIDTH // 2)
            player_y = player_data.get('position_y', SCREEN_HEIGHT // 2)
            for obj in game_state['objects']:
                draw_object(screen, obj, player_x, player_y, object_images)

        if player_data and game_state and 'bots' in game_state:
            player_x = player_data.get('position_x', SCREEN_WIDTH // 2)
            player_y = player_data.get('position_y', SCREEN_HEIGHT // 2)
            for bot in game_state['bots']:
                draw_bot(screen, bot, player_x, player_y, ghost_images)
        print(f"part5: {time.time() - start}")

        start = time.time()
        if player_image:
            draw_player(screen, player_image)
        print(f"part6: {time.time() - start}")

        start = time.time()
        status_text = font.render("Bot Visualization - Press ESC to exit", True, WHITE)
        screen.blit(status_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)
        print(f"loop: {time.time() - start}")

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
