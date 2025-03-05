import pygame

# Initialize Pygame
pygame.init()

# Constants
TILE_SIZE = 64  # Size of each tile in pixels

# Map Layout: A 2D list where each number represents a specific tile type
# 1 = Wall, 0 = Floor, 2 = Special tile
MAP_LAYOUT = [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 2, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1],
]

# Load tile images and scale them to the correct size
try:
    WALL_IMAGE = pygame.image.load("grass8.png")
    FLOOR_IMAGE = pygame.image.load("grass8.png")
    SPECIAL_IMAGE = pygame.image.load("grass8.png")

    # Scale images to fit the tile size
    WALL_IMAGE = pygame.transform.scale(WALL_IMAGE, (TILE_SIZE, TILE_SIZE))
    FLOOR_IMAGE = pygame.transform.scale(FLOOR_IMAGE, (TILE_SIZE, TILE_SIZE))
    SPECIAL_IMAGE = pygame.transform.scale(SPECIAL_IMAGE, (TILE_SIZE, TILE_SIZE))
except pygame.error as e:
    print(f"Error loading images: {e}")
    pygame.quit()
    exit()

# Calculate the screen dimensions based on the map size
SCREEN_WIDTH = len(MAP_LAYOUT[0]) * TILE_SIZE
SCREEN_HEIGHT = len(MAP_LAYOUT) * TILE_SIZE

# Create the Pygame window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Map Example")

def draw_map():
    """
    Draw the map on the screen by looping through the MAP_LAYOUT.
    Each tile is drawn based on its corresponding value in the layout.
    """
    for row_index, row in enumerate(MAP_LAYOUT):
        for col_index, tile in enumerate(row):
            # Calculate the position of the tile on the screen
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE

            # Draw the appropriate tile image
            if tile == 1:
                screen.blit(WALL_IMAGE, (x, y))
            elif tile == 0:
                screen.blit(FLOOR_IMAGE, (x, y))
            elif tile == 2:
                screen.blit(SPECIAL_IMAGE, (x, y))

def main():
    """
    Main game loop that handles events, updates the screen, and draws the map.
    """
    running = True  # Boolean to control the game loop

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen
        screen.fill((0, 0, 0))  # Black background

        # Draw the map
        draw_map()

        # Update the display
        pygame.display.flip()

    # Quit Pygame when the game loop ends
    pygame.quit()

# Run the main game loop
if _name_ == "_main_":
    main()
