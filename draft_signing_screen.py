import pygame

HOME_SCREEN = 'screens\\HomeScreen1.0.png'
INSTRUCTION1 = 'screens\\InstructionsA1.0.jpg'
INSTRUCTION2 = 'screens\\InstructionsB1.0.jpg'
SIGNING = 'screens\\SigningScreen1.0.png'
LOGIN = 'screens\\LoginScreen1.0.png'

# mouse:
LEFT = 1
SCROLL = 2
RIGHT = 3
WHITE = (255,255,255)
RED = (139,0,0)

# original resolution
BASE_WIDTH = 1280
BASE_HEIGHT = 800

def scale_rect(x1, y1, x2, y2, screen_width, screen_height):
    scale_x = screen_width / BASE_WIDTH
    scale_y = screen_height / BASE_HEIGHT
    return (
        int(x1 * scale_x),
        int(y1 * scale_y),
        int(x2 * scale_x),
        int(y2 * scale_y)
    )

def in_scaled_area(x, y, x1, y1, x2, y2, sw, sh):
    sx1, sy1, sx2, sy2 = scale_rect(x1, y1, x2, y2, sw, sh)
    return sx1 < x < sx2 and sy1 < y < sy2

def home_screen(screen, screen_width, screen_height):
    image = pygame.image.load(HOME_SCREEN)
    image = pygame.transform.scale(image, (screen_width, screen_height))
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                x, y = pygame.mouse.get_pos()

                if in_scaled_area(x, y, 528, 246, 751, 338, screen_width, screen_height):
                    instructions1_screen(screen, screen_width, screen_height)
                elif in_scaled_area(x, y, 528, 361, 751, 453, screen_width, screen_height):
                    loging_screen(screen, screen_width, screen_height)
                elif in_scaled_area(x, y, 528, 482, 751, 574, screen_width, screen_height):
                    signing_screen(screen, screen_width, screen_height)
                elif in_scaled_area(x, y, 1204, 716, 1262, 781, screen_width, screen_height):
                    running = False

        screen.blit(image, (0, 0))
        pygame.display.update()

def instructions1_screen(screen, screen_width, screen_height):
    image = pygame.image.load(INSTRUCTION1)
    image = pygame.transform.scale(image, (screen_width, screen_height))
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                x, y = pygame.mouse.get_pos()
                if in_scaled_area(x, y, 49, 665, 109, 750, screen_width, screen_height):
                    instructions2_screen(screen, screen_width, screen_height)
                elif in_scaled_area(x, y, 1204, 716, 1262, 781, screen_width, screen_height):
                    running = False

        screen.blit(image, (0, 0))
        pygame.display.update()

def instructions2_screen(screen, screen_width, screen_height):
    image = pygame.image.load(INSTRUCTION2)
    image = pygame.transform.scale(image, (screen_width, screen_height))
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                x, y = pygame.mouse.get_pos()
                if in_scaled_area(x, y, 1204, 716, 1262, 781, screen_width, screen_height):
                    running = False

        screen.blit(image, (0, 0))
        pygame.display.update()

def loging_screen(screen, screen_width, screen_height):
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
                x, y = pygame.mouse.get_pos()
                if in_scaled_area(x, y, 1204, 716, 1262, 781, screen_width, screen_height):
                    running = False
                elif in_scaled_area(x, y, 217, 277, 1104, 362, screen_width, screen_height):
                    username_input_active = True
                    password_input_active = False
                elif in_scaled_area(x, y, 217, 409, 1104, 488, screen_width, screen_height):
                    username_input_active = False
                    password_input_active = True
                elif in_scaled_area(x, y, 217, 554, 465, 638, screen_width, screen_height):
                    username_input_active = False
                    password_input_active = False
                    # does_user_exist = authenticate_user(username_text, password_text)[0]
                    does_user_exist = False
                    if not does_user_exist:
                        error_text = "This User doesn't exist, check the Username or the Password"
                    else:
                        pass

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
        screen.blit(text_surface, scale_rect(490, 300, 490, 300, screen_width, screen_height)[:2])
        password_print = "*" * len(password_text)
        text_surface = font.render(password_print, True, WHITE)
        screen.blit(text_surface, scale_rect(480, 443, 480, 443, screen_width, screen_height)[:2])
        text_surface = font2.render(error_text, True, RED)
        screen.blit(text_surface, scale_rect(217, 510, 217, 510, screen_width, screen_height)[:2])
        pygame.display.update()

def signing_screen(screen, screen_width, screen_height):
    image = pygame.image.load(SIGNING)
    image = pygame.transform.scale(image, (screen_width, screen_height))
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
                x, y = pygame.mouse.get_pos()
                if in_scaled_area(x, y, 1204, 716, 1262, 781, screen_width, screen_height):
                    running = False
                elif in_scaled_area(x, y, 217, 227, 1104, 306, screen_width, screen_height):
                    username_input_active = True
                    password_input_active = False
                    verification_input_active = False
                elif in_scaled_area(x, y, 217, 353, 1104, 431, screen_width, screen_height):
                    username_input_active = False
                    password_input_active = True
                    verification_input_active = False
                elif in_scaled_area(x, y, 217, 477, 1104, 556, screen_width, screen_height):
                    username_input_active = False
                    password_input_active = False
                    verification_input_active = True
                elif in_scaled_area(x, y, 217, 605, 465, 686, screen_width, screen_height):
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
        screen.blit(font.render(username_text, True, WHITE), scale_rect(490, 245, 490, 245, screen_width, screen_height)[:2])
        screen.blit(font.render("*" * len(password_text), True, WHITE), scale_rect(480, 385, 480, 385, screen_width, screen_height)[:2])
        screen.blit(font.render("*" * len(verification_text), True, WHITE), scale_rect(760, 510, 760, 510, screen_width, screen_height)[:2])
        screen.blit(font2.render(error_text, True, RED), scale_rect(217, 575, 217, 575, screen_width, screen_height)[:2])
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
