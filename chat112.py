import pygame
from pyasn1.debug import Printer
from ChatClient import ChatClient

import buttons
import json
import requests
LEFT = 1
INVENTORY_ICON = "graphic\Inventory_Icon.png"
EXIT_ICON = "graphic\Exit_Icon.png"
CHAT_ICON = "graphic\Chat_Icon.png"
MINI_MAP_ICON = "graphic\Map_Icon.png"
MONEY_ICON = "graphic\Money_Show.png"
NOT_OPEN_INVENTORY = r"graphic\Not_Open_Inventory.png"
FULL_INVENTORY_ITEMS = r"graphic\Full_Inventory_Items.png"
FULL_INVENTORY_SHOP = r"graphic\Full_Inventory_Shop.png"
FULL_HP_BAR = "graphic\Hp_Bar.png"
CHAT_WINDOW_LAYER_1 = "graphic\Chat_First_Layer.png"
CHAT_WINDOW_LAYER_2 = "graphic\Chat_Second_Layer.png"
CURRENT_HOLDING = "graphic\Current_Holding.png"
MINI_BUTTON_PRESSED = "graphic\Mini_Button_Pressed.png"
MINI_BUTTON_NOT_PRESSED = "graphic\Mini_Button_Not_Pressed.png"
DELETE_BUTTON = "graphic\Delete_Button.png"

# colors:
WHITE = (255,255,255)
BACK = (182,212,137)
MONEY_TEXT = (129,69,37)

# Your API URL
API_URL = 'http://127.0.0.1:5000'
TOKEN = ""

clock = pygame.time.Clock()
frames_per_second = 30
window_height = 720
window_width = 1280

# flags:

display = pygame.display.set_mode((window_width, window_height))
display.fill(BACK)

def handle_chat_message(message):
    """Callback function to handle incoming chat messages"""
    print("Handling the Chat Message")
    global received_messages
    if not hasattr(handle_chat_message, 'received_messages'):
        handle_chat_message.received_messages = []
    print("befor cheaking if chat")
    print(message['type'])
    print(message['content'])
    if message['type'] == 'chat':
        print("message is chat")
        del messegas[0]
        messegas.append(message['content'])
        del users[0]
        users.append(message['client_name'])


pygame.init()

client = ChatClient('localhost',5005,handle_chat_message)
client.connect("user")
client.start()

TEXT = ""
TEXT_ACTIVE = False
messegas = [" ", " ", " ", " ", " ", "  ", " ", " "]
users = [" ", " ", " ", " ", " ", "  ", " ", " "]



CHAT_OPEN = 0 #BOOLEAN OF NUMBERS- odd=open, even=close


def open_chat(display):
    """
    opens the chat window
    """
    global TEXT
    global TEXT_ACTIVE
    global chat_client

    # Initialize chat client if not already done
   # if not hasattr(open_chat, 'receive_thread'):

    # Draw chat window layers
    open_chat_first_layer_image = pygame.image.load(CHAT_WINDOW_LAYER_1).convert_alpha()
    open_chat_first_layer_image.set_colorkey(WHITE)
    open_chat_first_layer_image.set_alpha(180)
    chat_first_layer = buttons.Button(810, 30, open_chat_first_layer_image)
    chat_first_layer.draw(display)

    open_chat_second_layer_image = pygame.image.load(CHAT_WINDOW_LAYER_2).convert()
    open_chat_second_layer_image.set_colorkey(WHITE)
    chat_second_layer = buttons.Button(810, 30, open_chat_second_layer_image)
    chat_second_layer.draw(display)

    #prints the messages on the chat
    font = pygame.font.Font(None, 20)
    count_print_text = 0
    count_messages = 0
    print_messages_y = 50
    while count_print_text < 8:
        the_message = users[count_messages] + ":   " + messegas[count_messages]
        #the_user = users[count_messages]
        text_surface = font.render(the_message, True, WHITE)
        text_position = (840, print_messages_y)
        display.blit(text_surface, text_position)
        count_print_text = count_print_text + 1
        count_messages = count_messages + 1
        print_messages_y = print_messages_y + 20



    # Display received messages
    font = pygame.font.Font(None, 20)
    if hasattr(handle_chat_message, 'received_messages'):
        y_offset = 50
        for msg in handle_chat_message.received_messages:
            text_surface = font.render(msg, True, WHITE)
            text_position = (840, y_offset)
            display.blit(text_surface, text_position)
            y_offset += 20

    font = pygame.font.Font(None, 20)
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
            x = pygame.mouse.get_pos()[0]
            y = pygame.mouse.get_pos()[1]


            if 834 < x < 1190 and 225 < y < 251:
                TEXT_ACTIVE = True
                print("true")

            if 1190 < x < 1226 and 225 < y < 251:
                print("send button")
                client.chat_message(TEXT)
                TEXT = ""


        if  TEXT_ACTIVE and event.type == pygame.KEYDOWN:   # and event.type == pygame.KEYDOWN
            print("yes")
            if event.key == pygame.K_BACKSPACE:
                TEXT = TEXT[:-1]
            elif len(TEXT) < 40:
                TEXT += event.unicode


    text_surface = font.render(TEXT, True, WHITE)
    text_position = (840, 235)
    display.blit(text_surface, text_position)

pygame.init()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    display.fill(BACK)
    open_chat(display)
    pygame.display.flip()
    clock.tick(30)
pygame.quit()
