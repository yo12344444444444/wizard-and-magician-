import pygame
import pytmx

pygame.init()

# Set up the display BEFORE loading the map
screen = pygame.display.set_mode((800, 600))

# Now load the TMX map
tmx_data = pytmx.load_pygame("mapyyEnd.tmx")

# Extract a tile image (ensure correct layer, x, and y)
tile_image = tmx_data.get_tile_image(0, 0, 0)

running = True
while running:
    screen.fill((0, 0, 0))  # Clear screen

    if isinstance(tile_image, pygame.Surface):  # Ensure it's a valid image
        screen.blit(tile_image, (100, 100))  # Draw tile

    pygame.display.flip()  # Update screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
