import pygame

HOME_SCREEN = 'screens\HomeScreen1.0.png'
INSTRUCTION1 = 'screens\InstructionsA1.0.jpg'
INSTRUCTION2 = 'screens\InstructionsB1.0.jpg'

# mouse:
LEFT = 1
SCROLL = 2
RIGHT = 3


def home_screen(screen, screen_width, screen_height):
    """
    running the home screen
    """
    # photo load
    image = pygame.image.load(HOME_SCREEN)  # שים כאן את המיקום של התמונה שלך
    image = pygame.transform.scale(image, (screen_width, screen_height))  # משנה את הגודל של התמונה לפי גודל המסך
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]

                # to instructions1 screen
                if 528 < x < 751 and 246 < y < 338:
                    instructions1_screen(screen, screen_width, screen_height)

                # to log in screen
                elif 528 < x < 751 and 361 < y < 453:
                    logging_screen(screen, screen_width, screen_height)

                # to sign up screen
                elif 528 < x < 751 and 482 < y < 574:
                    signing_screen(screen, screen_width, screen_height)

                # exist the game
                elif 1204 < x < 1262 and 716 < y < 781:
                    running = False

        screen.blit(image, (0, 0))
        pygame.display.update()



def instructions1_screen(screen, screen_width, screen_height):
    """
        running the first screen of the instructions
    """
    image = pygame.image.load(INSTRUCTION1)  # שים כאן את המיקום של התמונה שלך
    image = pygame.transform.scale(image, (screen_width, screen_height))  # משנה את הגודל של התמונה לפי גודל המסך
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]

                # to instruction 2 screen
                if 49 < x < 109 and 665 < y < 750:
                    instructions2_screen(screen, screen_width, screen_height)

                # return back (to home screen)
                elif 1204 < x < 1262 and 716 < y < 781:
                    running = False

        screen.blit(image, (0, 0))
        pygame.display.update()


def instructions2_screen(screen, screen_width, screen_height):
    """
        running the second screen of the instructions
    """
    image = pygame.image.load(INSTRUCTION2)  # שים כאן את המיקום של התמונה שלך
    image = pygame.transform.scale(image, (screen_width, screen_height))  # משנה את הגודל של התמונה לפי גודל המסך
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]

                # return back (to instruction 1 screen)
                if 1204 < x < 1262 and 716 < y < 781:
                    running = False
        screen.blit(image, (0, 0))
        pygame.display.update()


def logging_screen(screen, screen_width, screen_height):
    print("success 2!")


def signing_screen(screen, screen_width, screen_height):
    print("success 3!")


def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("game")
    screen_width, screen_height = pygame.display.get_surface().get_size()
    home_screen(screen, screen_width, screen_height)
    pygame.quit()

if __name__ == "__main__":
    main()