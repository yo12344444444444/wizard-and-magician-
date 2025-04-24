import pygame
from pyasn1.debug import Printer

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Mouse Button Events")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            print(event.type)
            if event.button == 1:  # כפתור שמאלי
                print("Left button DOWN")
            elif event.button == 3:  # כפתור ימני
                print("Right button DOWN")

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # כפתור שמאלי
                print("Left button UP")
            elif event.button == 3:  # כפתור ימני
                print("Right button UP")

    screen.fill((255, 255, 255))
    pygame.display.flip()

pygame.quit()