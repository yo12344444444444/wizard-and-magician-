import pygame

WINDOW_WIDTH = 732                  #change the size
WINDOW_HEIGHT = 1200                #change the size
pygame.init()
size = (WINDOW_WIDTH, WINDOW_HEIGHT)

IMAGE = 'grass4.jpg'
img = pygame.image.load(IMAGE)

screen = pygame.display.set_mode(size)
screen.blit(img, (0, 0))
pygame.display.set_caption("Game")


pygame.display.flip()

lop=0
while lop < 20000:
    lop = lop+1
    lop2 = 0
    while lop2 < 20000:
        lop2 = lop2+1


def back():



pygame.quit()

