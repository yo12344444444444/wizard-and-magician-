import pygame
from pyasn1.debug import Printer

import buttons
import json
import requests

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
INVENTORY_OPEN_ITEMS = 0 #BOOLEAN OF NUMBERS- odd=full_inventory, even=not full inventory
INVENTORY_OPEN_SHOP = 0 #BOOLEAN OF NUMBERS- odd=full_inventory, even=not full inventory
CHAT_OPEN = 0 #BOOLEAN OF NUMBERS- odd=open, even=close
CLICKED = False

display = pygame.display.set_mode((window_width, window_height))
display.fill(BACK)

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

    # holding icon:
    current_holding_image = pygame.image.load(CURRENT_HOLDING).convert()
    current_holding_image .set_colorkey(WHITE)
    current_holding = buttons.Button(150, 570, current_holding_image)

    # money icon:
    money_image = pygame.image.load(MONEY_ICON).convert()
    money_image.set_colorkey(WHITE)
    money_icon = buttons.Button(1110, 654, money_image)

    return inventory_icon,mini_map_icon,exit_icon,chat_icon,current_holding, money_icon


def put_icons_on_screen(display,inventory_icon, mini_map_icon, exit_icon, chat_icon,current_holding,money_icon, event):
    """
    prints on the screen the icons, the mini map frame
    """
    global INVENTORY_OPEN_ITEMS
    global INVENTORY_OPEN_SHOP
    global CHAT_OPEN
    global CLICKED

    if exit_icon.draw(display):
        return False

    if chat_icon.draw(display):
        CHAT_OPEN += 1

    if CHAT_OPEN % 2 == 1:
        open_chat()

    if inventory_icon.draw(display):
        INVENTORY_OPEN_ITEMS += 1
        INVENTORY_OPEN_SHOP = 0

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not CLICKED:
        x, y = pygame.mouse.get_pos()
        CLICKED = True
        if 125 < y < 215 and 480 < x < 570:
            INVENTORY_OPEN_SHOP += 1
            INVENTORY_OPEN_ITEMS += 1

        if 125 < y < 215 and 375 < x < 460:
            INVENTORY_OPEN_SHOP += 1
            INVENTORY_OPEN_ITEMS += 1

    if event.type == pygame.MOUSEBUTTONUP:
        CLICKED = False

    if INVENTORY_OPEN_ITEMS % 2 == 1:
        open_full_inventory_items(display)

    if INVENTORY_OPEN_SHOP % 2 == 1:
        open_full_inventory_shop(display)

    if INVENTORY_OPEN_ITEMS % 2 == 0 and INVENTORY_OPEN_SHOP % 2 == 0:
        open_not_full_inventory(display)

    money_icon.draw(display)
    # money = get_coins()
    font = pygame.font.Font(None, 35)
    money = 1000
    amount = font.render( str(money), True, MONEY_TEXT)
    display.blit(amount, (1168, 667))

    mini_map_icon.draw(display)
    current_holding.draw(display)
    print_current_holding(display)
    return True


##########################################################################################################
# open windows:

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


def open_full_inventory_items(display):
    """
    draw full inventory open - items
    """
    global CLICKED


    open_full_inventory_image = pygame.image.load(FULL_INVENTORY_ITEMS).convert()
    open_full_inventory_image.set_colorkey(WHITE)
    full_inventory = buttons.Button(350, 119, open_full_inventory_image)
    full_inventory.draw(display)

    hp_bar_image = pygame.image.load(FULL_HP_BAR).convert()
    hp_bar_image.set_colorkey(WHITE)
    hp_bar_icon = buttons.Button(640, 170, hp_bar_image)
    hp_bar_icon.draw(display)
    draw_full_inventory_hp_bar(display)

    print_full_inventory(display)
    print_mini_buttons(display)
    print_delete_buttons(display)


def open_full_inventory_shop(display):
    """
    draw full inventory open - shop
    """
    global CLICKED

    open_full_inventory_image = pygame.image.load(FULL_INVENTORY_SHOP).convert()
    open_full_inventory_image.set_colorkey(WHITE)
    full_inventory = buttons.Button(350, 119, open_full_inventory_image)
    full_inventory.draw(display)

    hp_bar_image = pygame.image.load(FULL_HP_BAR).convert()
    hp_bar_image.set_colorkey(WHITE)
    hp_bar_icon = buttons.Button(640, 170, hp_bar_image)
    hp_bar_icon.draw(display)
    draw_full_inventory_hp_bar(display)


    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not CLICKED:
        x, y = pygame.mouse.get_pos()
        print("buy:",x,y)
        CLICKED = True

        if 815 < x < 900 and  375 < y < 410:
            print("you bought an iron sword!")

        elif 920 < x < 1005 and  375 < y < 410:
            print("you bought a gold sword!")

        elif 815 < x < 900 and 525 < y < 555:
            print("you bought a wood wand!")

        elif 920 < x < 1005 and 525 < y < 555:
            print("you bought a gold wand!")

    if event.type == pygame.MOUSEBUTTONUP:
        CLICKED = False

    print_full_inventory(display)
    print_mini_buttons(display)
    print_delete_buttons(display)


def open_not_full_inventory(display):
    """
    draw not full inventory
    """
    inventory_not_open_image = pygame.image.load(NOT_OPEN_INVENTORY).convert()
    inventory_not_open_image.set_colorkey(WHITE)
    inventory_not_open = buttons.Button(350, 570, inventory_not_open_image)
    inventory_not_open.draw(display)

    # hp bar:
    hp_bar_image = pygame.image.load(FULL_HP_BAR).convert()
    hp_bar_image.set_colorkey(WHITE)
    hp_bar_icon = buttons.Button(350, 520, hp_bar_image)
    hp_bar_icon.draw(display)
    draw_not_full_inventory_hp_bar(display)
    print_not_full_inventory(display)


##########################################################################################################
# print items and buttons:

def print_not_full_inventory(dispaly):
    """
    prints in the small inventory the items, the anoumt
    """
    font = pygame.font.Font(None, 25)
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)
    with open("items.json", "r") as file_items:
        data_items = json.load(file_items)
    for i in range(1,7):

        cell = data_cells["cells"][str(i)]
        item = cell["item"]
        quantity = cell["quantity"]
        x = cell["topleft_x"]
        y = cell["topleft_y"]
        mini_button = cell["mini_button_pressed?"]

        # draw the item:
        image_place = data_items["items"][item]["icon"]
        image = pygame.image.load(image_place).convert()
        image.set_colorkey(WHITE)
        cell = buttons.Button(x, y, image)
        if cell.draw(display):
            current_holding_change(i)
        # draw the amount:
        if data_items["items"][item]["stackable"]:
            amount = font.render(str(quantity), True, WHITE)
            dispaly.blit(amount, (x+77,y+3))


def print_full_inventory(dispaly):
    """
    prints in the full inventory the items
    :return:
    """
    font = pygame.font.Font(None, 25)
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)
    with open("items.json", "r") as file_items:
        data_items = json.load(file_items)
    for i in range(1,19):

        cell = data_cells["cells"][str(i)]
        item = cell["item"]
        quantity = cell["quantity"]
        x = cell["topleft_x"]
        y = cell["topleft_y"]
        mini_button = cell["mini_button_pressed?"]

        # draw the item:
        image_place = data_items["items"][item]["icon"]
        image = pygame.image.load(image_place).convert()
        image.set_colorkey(WHITE)
        cellp = buttons.Button(x, y, image)
        cellp.draw(display)

        # draw the amount:
        if data_items["items"][item]["stackable"]:
            amount = font.render(str(quantity), True, WHITE)
            dispaly.blit(amount, (x+77,y+3))


def print_current_holding(display):
    """
    drawing the current holding
    """
    global CLICKED
    font = pygame.font.Font(None, 25)
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)
    with open("items.json", "r") as file_items:
        data_items = json.load(file_items)
    # drawing the current holding:
    holding_cell = data_cells["cells"]["19"]  # holding cell
    cell = data_cells["cells"]["19"]["cell"]  # cell - number of the cell that the current holding holds
    held_cell = data_cells["cells"][cell]
    item = held_cell["item"]
    quantity = held_cell["quantity"]
    x = holding_cell["topleft_x"]
    y = holding_cell["topleft_y"]

    image_place = data_items["items"][item]["icon"]
    image = pygame.image.load(image_place).convert()
    image.set_colorkey(WHITE)
    cell = buttons.Button(x, y, image)
    if cell.draw(display) and not CLICKED:
        CLICKED = True
        if item == "6" or "7" or "8" or "10" or "11":
            delete_item_from_json(item,  data_cells["cells"]["19"]["cell"])

    if data_items["items"][item]["stackable"]:
        amount = font.render(str(quantity), True, WHITE)
        display.blit(amount, (x + 77, y + 3))


def print_mini_buttons(display):
    """
    draws the mini button when you open the full inventory
    """
    global CLICKED
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)


    for i in range(1, 19):

        cell = data_cells["cells"][str(i)]
        x = cell["topleft_x"]
        y = cell["topleft_y"]
        mini_button = cell["mini_button_pressed?"]
        # draw the mini button:
        if mini_button:
            button_image = pygame.image.load(MINI_BUTTON_PRESSED).convert()
            if 1 <= i <= 6:
                button = buttons.Button(x, y + 103, button_image)
            else:
                button = buttons.Button(x, y + 85, button_image)
            button.draw(display)
        else:

            button_image = pygame.image.load(MINI_BUTTON_NOT_PRESSED).convert()
            if 1 <= i <= 6:
                button = buttons.Button(x, y + 103, button_image)
            else:
                button = buttons.Button(x, y + 85, button_image)
            if button.draw(display) and not CLICKED:
                CLICKED = True
                mini_button_change(i)
                bool, cell1, cell2 = both_mini_button_pressed()
                if bool:
                    switch_items_in_inventory(cell1, cell2)


def print_delete_buttons(display):
    """
        draws the mini button when you open the full inventory
        """
    global CLICKED
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)

    for i in range(1, 19):

        cell = data_cells["cells"][str(i)]
        x = cell["topleft_x"]
        y = cell["topleft_y"]
        item = cell["item"]

        button_image = pygame.image.load(DELETE_BUTTON).convert()
        if 1 <= i <= 6:
            button = buttons.Button(x, y + 83, button_image)
        else:
            button = buttons.Button(x, y + 65, button_image)
        if button.draw(display) and not CLICKED:
            CLICKED = True
            delete_item_from_json(item,i)

##########################################################################################################
# switch and change things in inventory:

def current_holding_change(cell_num):
    """
    changing the item in the current holding
    """
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)

    data_cells["cells"]["19"]["cell"] = str(cell_num)

    with open("inventory.json", "w") as file_cells:
        json.dump(data_cells, file_cells, indent=4)


def mini_button_change(cell_num):
    """
    changing the value of the mini button in the json
    """
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)

    data_cells["cells"][str(cell_num)]["mini_button_pressed?"] = True

    with open("inventory.json", "w") as file_cells:
        json.dump(data_cells, (file_cells), indent=4)


def both_mini_button_pressed():
    """
    checks if there are two cells with mini button pressed
    if yes returns true, cell_num1, cell_num2
    if no returns false
    """
    cell_num1 = 0
    cell_num2 = 0
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)
    for i in range(1,19):
        if data_cells["cells"][str(i)]["mini_button_pressed?"] and cell_num1 == 0:
            cell_num1 = i
        if data_cells["cells"][str(i)]["mini_button_pressed?"] and cell_num1 != 0 and cell_num1 != i:
            cell_num2 = i
    print(cell_num1, cell_num2)
    if cell_num1 != 0 and cell_num2 != 0:
        return True, cell_num1, cell_num2
    return False, cell_num1, cell_num2


def switch_items_in_inventory(cell_num1, cell_num2):
    """
    switch cell num1 with cell num2
    """
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)

    item1 = data_cells["cells"][str(cell_num1)]["item"]
    quantity1 = data_cells["cells"][str(cell_num1)]["quantity"]

    item2 = data_cells["cells"][str(cell_num2)]["item"]
    quantity2 = data_cells["cells"][str(cell_num2)]["quantity"]

    # put in cell 1 the item of cell 2:
    data_cells["cells"][str(cell_num1)]["item"] = item2
    data_cells["cells"][str(cell_num1)]["quantity"] = quantity2

    # put in cell 2 the item of cell 1:
    data_cells["cells"][str(cell_num2)]["item"] = item1
    data_cells["cells"][str(cell_num2)]["quantity"] = quantity1

    for cell in data_cells["cells"].values():
        cell["mini_button_pressed?"] = False

    with open("inventory.json", "w") as file_cells:
        json.dump(data_cells, file_cells, indent=4)

    print(data_cells)


##########################################################################################################
# HP bar:

def draw_not_full_inventory_hp_bar(display):
    """
    print the white area of the hp bar when the inventory is not full
    """
    # hp = get_health()
    hp = 70
    # משהו שמבקש את הHP של השחקן מהשרת
    lack = 100 - hp
    width = int((379 * lack)/100)
    height = 22
    pygame.draw.rect(display, WHITE, (736-width, 528, width, height))


def draw_full_inventory_hp_bar(display):
    """
    print the white area of the hp bar when the inventory is full
    """
    # hp = get_health()
    hp = 70
    lack = 100 - hp
    width = int((379 * lack) / 100)
    height = 22
    pygame.draw.rect(display, WHITE, (1026 - width, 178, width, height))


##########################################################################################################
# delete things from inventory:


def delete_item_from_json(item,cell):
    """
    delete the item from the
    """
    with open("items.json", "r") as file_items:
        data_items = json.load(file_items)
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)

    if not data_items["items"][str(item)]["stackable"] or data_cells["cells"][str(cell)]["quantity"] == 1:
        data_cells["cells"][str(cell)]["quantity"] = 0
        data_cells["cells"][str(cell)]["item"] = "0"

    else:
        data_cells["cells"][str(cell)]["quantity"] -= 1

    with open("inventory.json", "w") as file_cells:
        json.dump(data_cells, file_cells, indent=4)


##########################################################################################################
# add items to inventory:

def check_inventory_fullness():
    """
    checks if the inventory is full or not.
    if he is full return true.
    if he is not full return false.
    """
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)

    for i in range(1,19):
        if data_cells["cells"][str(i)]["item"] == "0":
            return False
    return True


def item_exist_in_inventory(item):
    """
    check if the item exist in the inventory in case it is stackable
    param item: the id of the item
    if it does return true and the cell
    if it doesn't return false and zero
    """
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)

    for i in range(1,19):
        if data_cells["cells"][str(i)]["item"] == str(item):
            return True, i

    return False, 0


def add_item(item, amount):
    """
    param item: the id of the item
    param amount: the amount of the item
    add the item to inventory

    if the item cannot be added returns false.
    if it was added successfully returns true.
    """
    with open("items.json", "r") as file_items:
        data_items = json.load(file_items)
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)

    if data_items["items"][str(item)]["stackable"]:
        bool, cell = item_exist_in_inventory(item)
        if bool:
                quantity = data_cells["cells"][str(cell)]["quantity"]
                data_cells["cells"][str(cell)]["quantity"] = int(int(quantity) + int(amount))

    if check_inventory_fullness():
        print("full :(")
        return False

    for i in range(1, 19):
        if data_cells["cells"][str(i)]["item"] == "0":
            print("found place", i, str(item), int(amount))
            data_cells["cells"][str(i)]["item"] = str(item)
            data_cells["cells"][str(i)]["quantity"] = int(amount)
            break

    with open("inventory.json", "w") as file_cells:
        json.dump(data_cells, file_cells, indent=4)
    return True


##########################################################################################################
# get things from the server:


def get_player_state():
    headers = {'Authorization': f'Bearer {TOKEN}'}
    data = {'x': window_width, 'y': window_height}
    response = requests.post(f'{API_URL}/game_state', json=data, headers=headers)
    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        print("Error getting game state:", response.json())
        return None


def get_health():
    """
    get the health from the server and return it
    """
    data = get_player_state()
    return data["health"]


def get_coins():
    """
    get the health from the server and return it
    """
    data = get_player_state()
    return data["coins"]


##########################################################################################################
# send things to the server:

pygame.init()
inventory_icon, mini_map_icon, exit_icon, chat_icon,current_holding, money_icon = create_icons()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    display.fill(BACK)
    if not put_icons_on_screen(display,inventory_icon, mini_map_icon, exit_icon, chat_icon,current_holding, money_icon, event):
        running = False

    pygame.display.flip()
    clock.tick(30)
pygame.quit()