import pygame
import sys
import socket
import json

#HOST = '10.12.8.38'  # Localhost IP address
#PORT = '8821'  # Port number to connect to
#client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#client_socket.connect((HOST, int(PORT)))

#client_socket.send("Hello world!".encode('utf-8'))

# initialize it
pygame.init()

# configurations
frames_per_second = 30
window_height = 1080
window_width = 1920

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# creating window
display = pygame.display.set_mode((window_width, window_height))

img = pygame.image.load('img/lets tuch grass.png')
clock = pygame.time.Clock()
display.fill(WHITE)
display.blit(img, (0, 0))
class objectPlascer:
    def __init__(self, pos, id):
        print("hi")
        self.pos = pos
        self.id = id

    def put(self):
        # some JSON:
        with open("db.json", "r") as f:
            y = json.load(f)
        print(y["On map objects"][()])
#        display.blit(, (0, 0))
        display.blit()

def pacet_resive(pac):
    for i in pac:
        print(pac)
# forever loop
while True:
    # frame clock ticking
    clock.tick(frames_per_second)
#    print(client_socket.recv(1024))
    a = objectPlascer((22,22), 'a')
    a.put()
    pygame.display.flip()
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            client_socket.close()
