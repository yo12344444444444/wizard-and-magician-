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

# Your API URL
API_URL = 'http://127.0.0.1:5000'

# Pygame screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bot Visualization')

# Font for displaying text
font = pygame.font.SysFont('Arial', 16)

# Load the ghost images
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
        print(f"Error loading images: {e}")
        return None

# Load player image
def load_player_image():
    try:
        current_dir = os.getcwd()
        parent_dir = os.path.dirname(current_dir)
        player_path = os.path.join(parent_dir, 'graphic', 'Standing_front.png')
        print(f"Looking for player image at: {player_path}")
        return pygame.image.load(player_path)
    except pygame.error as e:
        print(f"Error loading player image: {e}")
        return None

# Function to call login API and get the token
def login(username, password):
    try:
        response = requests.post(f'{API_URL}/login', json={'username': username, 'password': password})
        if response.status_code == 200:
            return response.json()['token']
        else:
            print(f"Login failed: {response.status_code}", response.json())
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return None

# Function to get player data
def get_player_data(token):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{API_URL}/get_player', headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting player data: {response.status_code}", response.json())
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return None

# Function to get the game state
def get_game_state(token, screen_width, screen_height):
    #try:
        headers = {'Authorization': f'Bearer {token}'}
        data = {'screen_width': screen_width, 'screen_height': screen_height}
        response = requests.post(f'{API_URL}/game_state', json=data, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting game state: {response.status_code}")
            return None
    #except requests.exceptions.RequestException as e:
       # print(f"Connection error: {e}")
       # return None

# Draw a bot relative to the player
def draw_bot(screen, bot, player_x, player_y, ghost_images):
    bot_x = bot.get('x', 0)
    bot_y = bot.get('y', 0)
    direction = bot.get('direction', 'front').lower()

    # המיקום במסך הוא:
    bot_location_x = (bot_x - player_x) + (SCREEN_WIDTH // 2)
    bot_location_y = (bot_y - player_y) + (SCREEN_HEIGHT // 2)

    if direction in ('up', 'back'):
        ghost_img = ghost_images['back']
    elif direction in ('down', 'front'):
        ghost_img = ghost_images['front']
    elif direction == 'left':
        ghost_img = ghost_images['left']
    elif direction == 'right':
        ghost_img = ghost_images['right']
    else:
        ghost_img = ghost_images['front']

    img_rect = ghost_img.get_rect(center=(bot_location_x, bot_location_y))
    screen.blit(ghost_img, img_rect)

# Draw player at center
def draw_player(screen, player_image):
    # השחקן תמיד באמצע המסך
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    player_rect = player_image.get_rect(center=(center_x, center_y))
    screen.blit(player_image, player_rect)

# Main visualization function
def main():
    ghost_images = load_images()
    player_image = load_player_image()
    if not ghost_images or not player_image:
        print("Failed to load required images.")
        return

    username = '2212'
    password = '2212'
    token = login(username, password)
    if not token:
        print("Login failed, exiting...")
        return

    print("Login successful!")

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        game_state = get_game_state(token, SCREEN_WIDTH, SCREEN_HEIGHT)
        player_data = get_player_data(token)

        screen.fill(BLACK)

        if player_data:
            player_x = player_data.get('position_x', SCREEN_WIDTH // 2)
            player_y = player_data.get('position_y', SCREEN_HEIGHT // 2)

            # Draw bots relative to player
            if game_state and 'bots' in game_state:
                for bot in game_state['bots']:
                    draw_bot(screen, bot, player_x, player_y, ghost_images)

            # Draw player in center
            draw_player(screen, player_image)

        # UI Text
        status_text = font.render("Bot Visualization - Press ESC to exit", True, WHITE)
        screen.blit(status_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
