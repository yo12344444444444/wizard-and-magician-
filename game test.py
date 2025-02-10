import pygame
import pytmx
import os

# Initialize Pygame
pygame.init()

# Function to safely load the TMX map
def load_tmx_map(filename):
    try:
        return pytmx.load_pygame(filename)
    except Exception as e:
        print(f"Error loading TMX file: {e}")
        print("Make sure your tileset (.tsx) is in the correct location or embedded.")
        return None

# Load the TMX file
tmx_filename = "mapy.tmx"  # Make sure the path is correct
tmx_data = load_tmx_map(tmx_filename)

if tmx_data:
    # Get map details
    tile_width = tmx_data.tilewidth
    tile_height = tmx_data.tileheight
    map_width = tmx_data.width * tile_width
    map_height = tmx_data.height * tile_height

    # Create a Pygame window
    screen = pygame.display.set_mode((map_width, map_height))

    # Function to draw the map
    def draw_map():
        for layer in tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * tile_width, y * tile_height))

    # Main loop
    running = True
    while running:
        screen.fill((0, 0, 0))  # Clear the screen
        draw_map()  # Draw the map
        pygame.display.flip()  # Update the display

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

pygame.quit()
