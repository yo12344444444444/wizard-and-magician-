import pygame
import buttons

INVENTORY_ICON = "graphic\Inventory_Icon.png"
EXIT_ICON = "graphic\Exit_Icon.png"
CHAT_ICON = "graphic\Chat_Icon.png"
MINI_MAP_ICON = "graphic\Map_Icon.png"
NOT_OPEN_INVENTORY = r"graphic\Not_Open_Inventory.png"
FULL_INVENTORY = r"graphic\Full_Inventory.png"
FULL_HP_BAR = "graphic\Hp_Bar.png"
CHAT_WINDOW_LAYER_1 = "graphic\Chat_First_Layer.png"
CHAT_WINDOW_LAYER_2 = "graphic\Chat_Second_Layer.png"
WHITE = (255,255,255)
BACK = (182,212,137)

frames_per_second = 30
window_height = 720
window_width = 1280

INVENTORY_OPEN = 0 #BOOLEAN OF NUMBERS- odd=full_inventory, even=not full inventory
CHAT_OPEN = 0 #BOOLEAN OF NUMBERS- odd=open, even=close
display = pygame.display.set_mode((window_width, window_height))
display.fill(BACK)

def open_chat():
    """
    opens the chat window
    """
    open_chat_first_layer_image = pygame.image.load(CHAT_WINDOW_LAYER_1).convert_alpha()
    open_chat_first_layer_image.set_colorkey(WHITE)
    open_chat_first_layer_image.set_alpha(180)
    chat_first_layer = buttons.Button(810, 30, open_chat_first_layer_image)
    chat_first_layer.draw(display)

    open_chat_second_layer_image = pygame.image.load(CHAT_WINDOW_LAYER_2).convert()
    open_chat_second_layer_image.set_colorkey(WHITE)
    chat_second_layer = buttons.Button(810, 30, open_chat_second_layer_image)
    chat_second_layer.draw(display)

def open_full_inventory():
    """
    draw full inventory open - items
    """
    open_full_inventory_image = pygame.image.load(FULL_INVENTORY).convert()
    open_full_inventory_image.set_colorkey(WHITE)
    full_inventory = buttons.Button(300, 119, open_full_inventory_image)
    full_inventory.draw(display)

    hp_bar_image = pygame.image.load(FULL_HP_BAR).convert()
    hp_bar_image.set_colorkey(WHITE)
    hp_bar_icon = buttons.Button(590, 170, hp_bar_image)
    hp_bar_icon.draw(display)


def open_not_full_inventory():
    """
    draw not full inventory
    """
    inventory_not_open_image = pygame.image.load(NOT_OPEN_INVENTORY).convert()
    inventory_not_open_image.set_colorkey(WHITE)
    inventory_not_open = buttons.Button(300, 570, inventory_not_open_image)
    inventory_not_open.draw(display)

    # hp bar:
    hp_bar_image = pygame.image.load(FULL_HP_BAR).convert()
    hp_bar_image.set_colorkey(WHITE)
    hp_bar_icon = buttons.Button(300, 520, hp_bar_image)
    hp_bar_icon.draw(display)

def print_in_full_inventory():
    """
    prints in the full inventory the items
    :return:
    """
    pass

def create_icons():
    # inventory icon:
    inventory_image = pygame.image.load(INVENTORY_ICON).convert()
    inventory_image.set_colorkey(WHITE)
    inventory_icon = buttons.Button(370, 30, inventory_image)

    # mini map frame:
    mini_map_image = pygame.image.load(MINI_MAP_ICON).convert()
    mini_map_image.set_colorkey(WHITE)
    mini_map_icon = buttons.Button(30, 10, mini_map_image)

    # exit icon:
    exit_image = pygame.image.load(EXIT_ICON).convert()
    exit_image.set_colorkey(WHITE)
    exit_icon = buttons.Button(270, 30, exit_image)

    # chat icon:
    chat_image = pygame.image.load(CHAT_ICON).convert()
    chat_image.set_colorkey(WHITE)
    chat_icon = buttons.Button(470, 30, chat_image)

    return inventory_icon,mini_map_icon,exit_icon,chat_icon


def put_icons_on_screen(display,inventory_icon, mini_map_icon, exit_icon, chat_icon):
    """
    prints on the screen the icons, the mini map frame
    """
    global INVENTORY_OPEN
    global CHAT_OPEN

    if inventory_icon.draw(display):
        INVENTORY_OPEN += 1
    if INVENTORY_OPEN % 2 == 1:
        open_full_inventory()
    if INVENTORY_OPEN % 2 == 0:
        open_not_full_inventory()
    if exit_icon.draw(display):
        return False
    if chat_icon.draw(display):
        CHAT_OPEN +=1
    if CHAT_OPEN % 2 == 1:
        open_chat()
    mini_map_icon.draw(display)

    return True


inventory_icon, mini_map_icon, exit_icon, chat_icon = create_icons()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    display.fill(BACK)
    if not put_icons_on_screen(display,inventory_icon, mini_map_icon, exit_icon, chat_icon):
        running = False
    pygame.display.flip()
pygame.quit()