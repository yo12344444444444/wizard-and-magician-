import socket
import server.clientTest
import pygame
from server import clientTest
import requests
from lb.findy import findy
import sys, os

DEFAULT_BUFFER_SIZE = 35

HOME_SCREEN = 'screens\Home_Screen.png'
INSTRUCTION1 = 'screens\Instruction_1.png'
INSTRUCTION2 = 'screens\Instruction_2.png'
INSTRUCTION3 = 'screens\Instruction_3.png'
INSTRUCTION4 = 'screens\Instruction_4.png'
INSTRUCTION5 = 'screens\Instruction_5.png'
SIGNING = 'screens\Signing_Screen.png'
LOGIN = 'screens\Login_Screen.png'

# mouse:
LEFT = 1
SCROLL = 2
RIGHT = 3
WHITE = (255,255,255)
RED = (139,0,0)
PURPLE = (73,69,123)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def home_screen(screen, screen_width, screen_height):
    """
    running the home screen
    """
    # photo load
    image = pygame.image.load(resource_path(HOME_SCREEN))  # שים כאן את המיקום של התמונה שלך
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
                    token= loging_screen(screen, screen_width, screen_height)
                    print("homescreen login token: ", token)
                    if token:
                        return token

                # to sign up screen
                elif 525 < x < 740 and 450 < y < 530:
                    token = signing_screen(screen, screen_width, screen_height)
                    print("homescreen singup token: ",token)
                    if token:
                        return token

                # exist the game
                elif 1204 < x < 1262 and 640 < y < 700:
                    running = False

        screen.blit(image, (0, 0))
        pygame.display.update()



def instructions1_screen(screen, screen_width, screen_height):
    """
        running the first screen of the instructions
    """
    image = pygame.image.load(resource_path(INSTRUCTION1))  # שים כאן את המיקום של התמונה שלך
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
        running the first screen of the instructions
    """
    image = pygame.image.load(resource_path(INSTRUCTION2))  # שים כאן את המיקום של התמונה שלך
    image = pygame.transform.scale(image, (screen_width, screen_height))  # משנה את הגודל של התמונה לפי גודל המסך
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]


                # to instruction 3 screen
                if 49 < x < 109 and 600 < y < 685:
                    instructions3_screen(screen, screen_width, screen_height)

                #  to instruction 1 screen
                elif 1204 < x < 1262 and 640 < y < 700:
                    running = False

        screen.blit(image, (0, 0))
        pygame.display.update()


def instructions3_screen(screen, screen_width, screen_height):
    """
        running the first screen of the instructions
    """
    image = pygame.image.load(resource_path(INSTRUCTION3))  # שים כאן את המיקום של התמונה שלך
    image = pygame.transform.scale(image, (screen_width, screen_height))  # משנה את הגודל של התמונה לפי גודל המסך
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]


                # to instruction 4 screen
                if 49 < x < 109 and 600 < y < 685:
                    instructions4_screen(screen, screen_width, screen_height)

                #  to instruction 2 screen
                elif 1204 < x < 1262 and 640 < y < 700:
                    running = False

        screen.blit(image, (0, 0))
        pygame.display.update()


def instructions4_screen(screen, screen_width, screen_height):
    """
        running the first screen of the instructions
    """
    image = pygame.image.load(resource_path(INSTRUCTION4))  # שים כאן את המיקום של התמונה שלך
    image = pygame.transform.scale(image, (screen_width, screen_height))  # משנה את הגודל של התמונה לפי גודל המסך
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]


                # to instruction 5 screen
                if 49 < x < 109 and 600 < y < 685:
                    instructions5_screen(screen, screen_width, screen_height)

                #  to instruction 3 screen
                elif 1204 < x < 1262 and 640 < y < 700:
                    running = False

        screen.blit(image, (0, 0))
        pygame.display.update()


def instructions5_screen(screen, screen_width, screen_height):
    """
        running the first screen of the instructions
    """
    image = pygame.image.load(resource_path(INSTRUCTION5))  # שים כאן את המיקום של התמונה שלך
    image = pygame.transform.scale(image, (screen_width, screen_height))  # משנה את הגודל של התמונה לפי גודל המסך
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]

                #  to instruction 4 screen
                if 1204 < x < 1262 and 640 < y < 700:
                    running = False

        screen.blit(image, (0, 0))
        pygame.display.update()

def loging_screen(screen, screen_width, screen_height):
    """
            running the loging screen
        """
    image = pygame.image.load(resource_path(LOGIN))
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
                    token = enter_user(username_text,password_text)
                    print("login token: ",token)
                    if not token:
                        error_text = "This User doesn't exist, check the Username or the Password"
                    else:
                        return token


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

        text_surface = font.render(username_text, True, PURPLE)
        text_position = (490, 265)
        screen.blit(text_surface, text_position)

        password_print = "*" * len(password_text)
        text_surface = font.render(password_print, True, PURPLE)
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
    image = pygame.image.load(resource_path(SIGNING))  # שים כאן את המיקום של התמונה שלך
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
                    token = create_user(username_text, password_text)
                    print("token signup:",token)
                    if password_text != verification_text:
                        error_text = "The Password and the Verification aren't equal"
                    elif not token:
                        error_text = "This Username already exists, choose another one"
                    else:
                        return token

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

        text_surface = font.render(username_text, True, PURPLE)
        text_position = (490, 215)
        screen.blit(text_surface, text_position)

        password_print = "*" * len(password_text)
        text_surface = font.render(password_print, True, PURPLE)
        text_position = (480, 345)
        screen.blit(text_surface, text_position)

        verification_print = "*" * len(verification_text)
        text_surface = font.render(verification_print, True, PURPLE)
        text_position = (760, 460)
        screen.blit(text_surface, text_position)

        text_surface = font2.render(error_text, True, RED)
        text_position = (217, 517)
        screen.blit(text_surface, text_position)

        pygame.display.flip()

def create_user(username,password):
    token=signup(username, password)
    if not token:
        print("Login failed, exiting...")
        return None
    return token

#    global packed_data
    """
    sends to the mainserver packet with the username and password like this:
    create // username // password

    the server check if the username exist and return a packet like this:
    0 bit: 1 = exist and didn't do anything
           0 = doesn't exist and created a new user
    """
 #   packet = "create//" + username + "//" + password
#    packet = packet.encode()
#    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#    server_socket.sendto(packet, (IP, PORT))
#    packed_data, client_addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
#    server_socket.close()
    # packed_data = 1
#    if packed_data[0] == 1:
#        return False # the username already exists
#    return True

def enter_user(username,password):
    token=login(username, password)
    if not token:
        print("Login failed, exiting...")
        return None
    return token
#    global packed_data
    """
    sends to the mainserver packet with the username and password like this:
    enter // username // password

    the server check if the username exist and return a packet like this:
    0 bit: 1 = this user exist
           0 = this user doesn't exist
    """
    #packet = "enter//" + username + "//" + password
    #print(packet)
    #packet = packet.encode()
    #print(packet)
    #server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #server_socket.sendto(packet, (IP, PORT))
    #packed_data, client_addr = server_socket.recvfrom(DEFAULT_BUFFER_SIZE)
    #server_socket.close()
 #   packed_data = 1
#    print(packed_data)
#    if packed_data[0] == 0:
#        return False # the user doesn't exist
#    return True
# Login and get token
def login(username, password):
    try:
        response = requests.post(f'{API_URL}/login', json={'username': username, 'password': password})
        if response.status_code == 200:
            token = response.json().get('token')
            print(f"Login successful! Token: {token}")
            return token
        else:
            print(f"Login error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return None

def signup(username, password):
    try:
        url = f"{API_URL}/signup"
        response = requests.post(url, json={"username": username, "password": password})
        if response.status_code == 200:
            token = response.json().get("token")
            print(f"Signup successful! Token: {token}")
            return token
        else:
            print(f"Signup error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection error during signup: {e}")
        return None


def get_player_data(API_URL, token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{API_URL}/get_player', headers=headers)
    print(response.json())
    print(data)
    addr = data[str(response.json().get('server'))]
    API_URL = "http://" + addr[0] + ":" + str(addr[1])
    print(API_URL)
    return API_URL

def main(API_URL):
    pygame.init()
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Game")

    token = home_screen(screen, screen_width, screen_height)
    print("token main: ",token)
    API_URL = get_player_data(API_URL, token)
    print(API_URL)
    if token:
        print("Token received, starting the game...")
        c = clientTest.clientTest(apiUrl=API_URL, data=data)
        c.main(token)  # כאן תפעיל את הקליינט שלך עם הטוקן
    else:
        print("No token received, exiting.")

    pygame.quit()
def PortDefinder(port):
    port = port
    result = 0
    while result == 0:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('localhost', port))
        if result == 0:
            port += 1
    return port
if __name__ == "__main__":
    port = PortDefinder(4000)
    finder = findy()
    data = finder.main(port)
    addr = data['lb']
    API_URL= "http://" + addr[0] + ":" + str(addr[1])

    print(API_URL)
    main(API_URL)
