import pygame
import requests
import json

# Initialize Pygame
pygame.init()

# Constants for screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30

# Game colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Your API URL
API_URL = 'http://127.0.0.1:5000'

# Pygame screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Game Client')

# Load images
def load_image(file):
    try:
        return pygame.image.load(file)
    except pygame.error:
        print(f"Error loading image: {file}")
        return None

# Player class to represent the player
class Player(pygame.sprite.Sprite):
    def __init__(self, username, x, y, idle_frame, animation_frames):
        super().__init__()
        self.username = username
        self.x = x
        self.y = y
        self.idle_frame = idle_frame
        self.animation_frames = [load_image(frame) for frame in animation_frames]
        self.image = self.animation_frames[0]  # Start with idle image
        self.rect = self.image.get_rect(center=(x, y))
        self.current_frame = 0
        self.moving = False

    def update(self):
        # Update the image for animation
        if self.moving:
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.current_frame]
        else:
            self.image = self.idle_frame
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.center = (self.x, self.y)

# Bot class to represent a bot
class Bot(pygame.sprite.Sprite):
    def __init__(self, bot_type, x, y, animation_frames):
        super().__init__()
        self.x = x
        self.y = y
        self.bot_type = bot_type
        self.animation_frames = [load_image(frame) for frame in animation_frames]
        self.image = self.animation_frames[0]  # Start with the first frame
        self.rect = self.image.get_rect(center=(x, y))
        self.current_frame = 0

    def update(self):
        # Loop through the animation frames
        self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
        self.image = self.animation_frames[self.current_frame]
        self.rect = self.image.get_rect(center=(self.x, self.y))

# Function to call login API and get the token
def login(username, password):
    response = requests.post(f'{API_URL}/login', json={'username': username, 'password': password})
    if response.status_code == 200:
        data = response.json()
        return data['token']
    else:
        print("Login failed:", response.json())
        return None

# Function to call signup API and get the token
def signup(username, password):
    response = requests.post(f'{API_URL}/signup', json={'username': username, 'password': password})
    if response.status_code == 200:
        data = response.json()
        return data['token']
    else:
        print("Signup failed:", response.json())
        return None


# Function to get the game state
def get_game_state(token, screen_width, screen_height):
    headers = {'Authorization': f'Bearer {token}'}
    data = {'x': screen_width, 'y': screen_height}
    response = requests.post(f'{API_URL}/game_state', json=data, headers=headers)
    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        print("Error getting game state:", response.json())
        return None

# Main game loop
def main():
    username = '2212'  # Change this to your username
    password = '2212'  # Change this to your password

    token = login(username, password)
    if not token:
        print("Login failed, exiting...")
        return
    print('success')
    game_state = get_game_state(token, SCREEN_WIDTH, SCREEN_HEIGHT)
    print(game_state)

if __name__ == '__main__':
    main()
