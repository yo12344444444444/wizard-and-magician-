import pygame
import sys

# initialize it
pygame.init()

# configurations
frames_per_second = 30
window_height = 1920
window_width = 1080

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# creating window
display = pygame.display.set_mode((window_width, window_height))

# creating our frame regulator
clock = pygame.time.Clock()

# forever loop
while True:
  # frame clock ticking
  clock.tick(frames_per_second)
  
  # frame Drawing
  display.fill(WHITE)
  
  # event loop
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()
