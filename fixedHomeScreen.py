import pygame

HOME_SCREEN = 'screens\HomeScreen1.0.png'
INSTRUCTION1 = 'screens\InstructionsA1.0.jpg'
INSTRUCTION2 = 'screens\InstructionsB1.0.jpg'
SIGNING = 'screens\SigningScreen1.0.png'
LOGIN = 'screens\LoginScreen1.0.png'

# mouse:
LEFT = 1
SCROLL = 2
RIGHT = 3
WHITE = (255,255,255)
RED = (139,0,0)

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
                if 525 < x < 740 and 250 < y < 335:
                    instructions1_screen(screen, screen_width, screen_height)

                # to log in screen
                elif 525 < x < 740 and 350 < y < 430:
                    loging_screen(screen, screen_width, screen_height)

                # to sign up screen
                elif 525 < x < 740 and 450 < y < 530:
                    signing_screen(screen, screen_width, screen_height)

                # exist the game
                elif 1204 < x < 1262 and 640 < y < 700:
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
                if 49 < x < 109 and 600 < y < 685:
                    instructions2_screen(screen, screen_width, screen_height)

                # return back (to home screen)
                elif 1204 < x < 1262 and 640 < y < 700:
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
                if 1204 < x < 1262 and 640 < y < 700:
                    running = False
        screen.blit(image, (0, 0))
        pygame.display.update()


def loging_screen(screen, screen_width, screen_height):
    """
            running the loging screen
        """
    image = pygame.image.load(LOGIN)
    image = pygame.transform.scale(image, (screen_width, screen_height))
    running = True

    username_text = ""
    password_text = ""
    error_text = ""

    username_input_active = False
    password_input_active = False

    font = pygame.font.Font(None, 70)
    font2 = pygame.font.Font(None, 35)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]


                # return back (to home screen)
                if 1204 < x < 1262 and 640 < y < 700:
                    running = False

                # username
                elif 217 < x < 1104 and 250 < y < 330:
                    username_input_active = True
                    password_input_active = False

                # password
                elif 217 < x < 1104 and 370 < y < 440:
                    username_input_active = False
                    password_input_active = True

                # enter user
                elif 217 < x < 465 and 500 < y < 575:
                    username_input_active = False
                    password_input_active = False
                    # does_user_exist = authenticate_user(username_text, password_text)[0]
                    does_user_exist = False
                    if not does_user_exist:
                        error_text = "This User doesn't exist, check the Username or the Password"
                    else:
                        pass
                    # enter game

            elif username_input_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    username_text = username_text[:-1]
                elif len(username_text) < 10:
                    username_text += event.unicode


            elif password_input_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    password_text = password_text[:-1]
                elif len(password_text) < 10:
                    password_text += event.unicode


        screen.blit(image, (0, 0))

        text_surface = font.render(username_text, True, WHITE)
        text_position = (490, 265)
        screen.blit(text_surface, text_position)

        password_print = "*" * len(password_text)
        text_surface = font.render(password_print, True, WHITE)
        text_position = (480, 395)
        screen.blit(text_surface, text_position)

        text_surface = font2.render(error_text, True, RED)
        text_position = (217, 465)
        screen.blit(text_surface, text_position)

        pygame.display.update()


def signing_screen(screen, screen_width, screen_height):
    """
            running the signing screen
        """
    image = pygame.image.load(SIGNING)  # שים כאן את המיקום של התמונה שלך
    image = pygame.transform.scale(image, (screen_width, screen_height))  # משנה את הגודל של התמונה לפי גודל המסך
    running = True

    username_text = ""
    password_text = ""
    verification_text = ""
    error_text = ""

    username_input_active = False
    password_input_active = False
    verification_input_active = False

    font = pygame.font.Font(None, 70)
    font2 = pygame.font.Font(None, 35)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]


                # return back (to home screen)
                if 1204 < x < 1262 and 640 < y < 700:
                    running = False

                # username
                elif 217 < x < 1104 and 200 < y < 280:
                    username_input_active = True
                    password_input_active = False
                    verification_input_active = False

                # password
                elif 217 < x < 1104 and 315 < y < 390:
                    username_input_active = False
                    password_input_active = True
                    verification_input_active = False

                # verification
                elif 217 < x < 1104 and 430 < y < 500:
                    username_input_active = False
                    password_input_active = False
                    verification_input_active = True

                # create user
                elif 217 < x < 465 and 545 < y < 620:
                    username_input_active = False
                    password_input_active = False
                    verification_input_active = False
                    # does_username_exist = authenticate_user(username_text, password_text)[0]
                    does_username_exist = False
                    if password_text != verification_text:
                        error_text = "The Password and the Verification aren't equal"
                    elif does_username_exist:
                        error_text = "This Username already exists, choose another one"
                    else:
                        pass
                    # create user

            elif username_input_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    username_text = username_text[:-1]
                elif len(username_text) < 10:
                    username_text += event.unicode


            elif password_input_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    password_text = password_text[:-1]
                elif len(password_text) < 10:
                    password_text += event.unicode


            elif verification_input_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    verification_text = verification_text[:-1]
                elif len(verification_text) < 10:
                    verification_text += event.unicode

        screen.blit(image, (0, 0))

        text_surface = font.render(username_text, True, WHITE)
        text_position = (490, 215)
        screen.blit(text_surface, text_position)

        password_print = "*" * len(password_text)
        text_surface = font.render(password_print, True, WHITE)
        text_position = (480, 345)
        screen.blit(text_surface, text_position)

        verification_print = "*" * len(verification_text)
        text_surface = font.render(verification_print, True, WHITE)
        text_position = (760, 460)
        screen.blit(text_surface, text_position)

        text_surface = font2.render(error_text, True, RED)
        text_position = (217, 517)
        screen.blit(text_surface, text_position)

        pygame.display.flip()


def authenticate_user(username, password):
    pass


def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("game")
    screen_width, screen_height = pygame.display.get_surface().get_size()
    home_screen(screen, screen_width, screen_height)
    pygame.quit()

if __name__ == "__main__":
    main()