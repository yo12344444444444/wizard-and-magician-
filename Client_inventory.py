import pygame
import requests
import sys
import time
import os
import buttons
import json

from server.Game2 import TOKEN

# Initialize Pygame
pygame.init()

# Constants for screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
window_height = 720
window_width = 1280
FPS = 30

# Files:
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

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACK = (182,212,137)
MONEY_TEXT = (129,69,37)

# Flags:
INVENTORY_OPEN_ITEMS = 0 #BOOLEAN OF NUMBERS- odd=full_inventory, even=not full inventory
INVENTORY_OPEN_SHOP = 0 #BOOLEAN OF NUMBERS- odd=full_inventory, even=not full inventory
CHAT_OPEN = 0 #BOOLEAN OF NUMBERS- odd=open, even=close
CLICKED = False

# Your API URL
API_URL = 'http://127.0.0.1:5000'

# Pygame screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bot Visualization')

# Font for displaying text
font = pygame.font.SysFont('Arial', 16)

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
        open_chat(display)

    if inventory_icon.draw(display):
        INVENTORY_OPEN_ITEMS += 1
        INVENTORY_OPEN_SHOP = 0

    money_icon.draw(display)
    money = get_coins()
    font = pygame.font.Font(None, 35)
    amount = font.render( str(money), True, MONEY_TEXT)
    display.blit(amount, (1168, 667))

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not CLICKED:
        x, y = pygame.mouse.get_pos()

        if 125 < y < 215 and 480 < x < 570:
            CLICKED = True
            INVENTORY_OPEN_SHOP += 1
            INVENTORY_OPEN_ITEMS += 1

        if 125 < y < 215 and 375 < x < 460:
            CLICKED = True
            INVENTORY_OPEN_SHOP += 1
            INVENTORY_OPEN_ITEMS += 1

    if INVENTORY_OPEN_ITEMS % 2 == 1:
        open_full_inventory_items(display,event)

    elif INVENTORY_OPEN_SHOP % 2 == 1:
        open_full_inventory_shop(display,event)

    elif INVENTORY_OPEN_ITEMS % 2 == 0 and INVENTORY_OPEN_SHOP % 2 == 0:
        open_not_full_inventory(display,event)

    if event.type == pygame.MOUSEBUTTONUP:
        CLICKED = False

    mini_map_icon.draw(display)
    current_holding.draw(display)
    print_current_holding(display,event)
    return True


##########################################################################################################
# open windows:

def open_chat(display):
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


def open_full_inventory_items(display,event):
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

    print_full_inventory(display,event)
    print_mini_buttons(display,event)
    print_delete_buttons(display,event)


def open_full_inventory_shop(display,event):
    """
    draw full inventory open - shop
    """
    global CLICKED
    money = get_coins()
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

        if 815 < x < 900 and 375 < y < 410 and money >= 200:
            CLICKED = True
            if buy_item("2", 200):
                add_item("2",1)
                print("you bought an iron sword!")
            else:
                print("not enough money or inventory is full")


        elif 920 < x < 1005 and 375 < y < 410 and money >= 300:
            CLICKED = True
            if buy_item("3", 300):
                add_item("3", 1)
                print("you bought a gold sword!")
            else:
                print("not enough money or inventory is full")


        elif 815 < x < 900 and 525 < y < 555 and money >= 200:
            CLICKED = True
            if buy_item("4", 200):
                add_item("4", 1)
                print("you bought a wood wand!")
            else:
                print("not enough money or inventory is full")


        elif 920 < x < 1005 and 525 < y < 555 and money >= 500:
            CLICKED = True
            if buy_item("5", 500):
                add_item("5", 1)
                print("you bought a gold wand!")
            else:
                print("not enough money or inventory is full")

    print_full_inventory(display,event)
    print_mini_buttons(display,event)
    print_delete_buttons(display,event)


def open_not_full_inventory(display,event):
    """
    draw not full inventory
    """
    global CLICKED

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
    print_not_full_inventory(display,event)


##########################################################################################################
# print items and buttons:

def print_not_full_inventory(display,event):
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
            display.blit(amount, (x+77,y+3))


def print_full_inventory(display,event):
    """
    prints in the full inventory the items
    :return:
    """
    global CLICKED
    if event.type == pygame.MOUSEBUTTONUP:
        CLICKED = False

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
            display.blit(amount, (x+77,y+3))


def print_current_holding(display,event):
    """
    drawing the current holding
    """
    global CLICKED
    if event.type == pygame.MOUSEBUTTONUP:
        CLICKED = False

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
        if item != "0" or "1" or "2" or "3" or "4" or "5" or "12" or "13" or "14":
            send_use_object(item)
        if item == "6" or "7" or "8" or "10" or "11":
            delete_item_from_json(item,  data_cells["cells"]["19"]["cell"])

    if data_items["items"][item]["stackable"]:
        amount = font.render(str(quantity), True, WHITE)
        display.blit(amount, (x + 77, y + 3))


def print_mini_buttons(display,event):
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


def print_delete_buttons(display,event):
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
            if item != "0":
                delete_item_from_json(item,i)
                delete_item_inventory(item,i)

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
    hp = get_health()
    # משהו שמבקש את הHP של השחקן מהשרת
    lack = 100 - hp
    width = int((379 * lack)/100)
    height = 22
    pygame.draw.rect(display, WHITE, (736-width, 528, width, height))


def draw_full_inventory_hp_bar(display):
    """
    print the white area of the hp bar when the inventory is full
    """
    hp = get_health()
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
            add_item_inventory(item, i, True)
            break

    with open("inventory.json", "w") as file_cells:
        json.dump(data_cells, file_cells, indent=4)
    return True


def look_for_empty_slot():
    """
    checks if there is an empty slot in the inventory
    if yes return its index and if not return 0
    """
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)

    for i in range(1,19):
        if data_cells["cells"][str(i)]["item"] == "0":
            return i
    return 0
##########################################################################################################
# build inventory:

def enter_inventory_data_to_json():
    """
    בדקתי ועובד
    gets the inventory from the function get_inventory_from_server
    and put it inside the json file the user have
    """
    with open("items.json", "r") as file_items:
        data_items = json.load(file_items)
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)

    data = get_inventory_from_server()
    if data is None:
        print("got no data")
    else:
        for i in range(18):
            item = next((item for item in data if item['slot_index'] == i), None)
            if item:
                name = item['name']
                id = name_to_id(name)
                quantity = item['quantity']
            else:
                id = "0"
                quantity = 0
            try:
                data_cells["cells"][str(i+1)]["item"] = str(id)
                data_cells["cells"][str(i+1)]["quantity"] = int(quantity)
            except Exception as e:
                print("error:", e)

        with open("inventory.json", "w") as file_cells:
            json.dump(data_cells, file_cells, indent=4)


def id_to_name(item_id):
    """
    get the id of the item as string and return its name
    """
    id_map = {
        "1": "Stone_Sword",
        "2": "Iron_Wand",
        "3": "Gold_Sword",
        "4": "Wood_Wand",
        "5": "Gold_Wand",
        "6": "Dark_Potion",
        "7": "Life_Potion",
        "8": "Fire_Potion",
        "10": "apple",
        "11": "blueberry",
    }
    return id_map.get(item_id)


def name_to_id(item_name):
    """
    Get the name of the item and return its id as string
    """
    name_map = {
        "Stone_Sword": "1",
        "Iron_Wand": "2",
        "Gold_Sword": "3",
        "Wood_Wand": "4",
        "Gold_Wand": "5",
        "Dark_Potion": "6",
        "Life_Potion": "7",
        "Fire_Potion": "8",
        "apple": "10",
        "blueberry": "11",
    }
    return name_map.get(item_name)


##########################################################################################################
# get things from the server:

def get_inventory_from_server():
    url = 'http://localhost:5000/get_inventory'
    headers = {
        'Authorization': f'Bearer {TOKEN}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(data['inventory'])
        return data['inventory']
    else:
        print("Error in get data inventory:", response.status_code, response.text)
        return None


def get_player_state():
    """
    Send GET request to /get_player and return the player's state.
    :param token: JWT token as string (without 'Bearer ')
    :param server_url: Base URL of the server
    :return: dict of player state or None if failed
    """
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    response = requests.get(f"{API_URL}/get_player", headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        print("Unauthorized: Invalid or expired token.")
    elif response.status_code == 404:
        print("Player not found.")
    else:
        print(f"Error: {response.status_code} - {response.text}")

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

def buy_item(item_id, money):
    """
    sends to the server what is the item that you bought, the amount of money it costs
    and where to put it
    if the inventory is full return False
    if it sent it successfully return True
    """
    slot_index = look_for_empty_slot()
    if slot_index == 0:
        return False
    else:
        url = 'http://localhost:5000/buy_object'  # שנה בהתאם לכתובת השרת שלך
        headers = {
            'Authorization': f'Bearer {TOKEN}',
            'Content-Type': 'application/json'
        }
        data = {
            'object_name': str(item_id),
            'amount': money,
            'slot_index': slot_index
        }
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return True


def add_item_inventory(object_id, slot_index, has_space):
    """

    :return:
    """
    object_name = id_to_name(object_id)
    if object_name is None:
        print(f"Invalid object_id: {object_id}")
        return None
    url = f"{API_URL}/add-to-inventory"
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        "has_space_in_inventory": has_space,
        "object_name": object_name,
        "slot_index": slot_index
        }
    print("hayo",data)
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"Server Response: {result['message']}")
            return result
        elif response.status_code == 404:
            print("Object not found on the map.")
        elif response.status_code == 400:
            print("Bad request: Missing or invalid data.",response)
        elif response.status_code == 401:
            print("Unauthorized: Invalid or missing token.")
        else:
            print(f"Unexpected error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")


def send_use_object(item):
    """
     sends to the server which object is in use
    :param item:
    :return:
    """
    url = f"{API_URL}/use_object"
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'object_type': item
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['effect']}")
            return result['effect']
        else:
            print(f"Failed to use object: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")
        return None


def delete_item_inventory(object_id, slot_index):
    """

    :param object_id:
    :param slot_index:
    :return:
    """
    pass
##########################################################################################################
# client not inventory:

# Load the ghost images
def load_images():
    try:
        current_dir = os.getcwd()
        parent_dir = os.path.dirname(current_dir)
        base_path = os.path.join(parent_dir, 'graphic', 'bot')
        print(f"Looking for images in: {base_path}")

        ghost_images = {
            'front': pygame.image.load('graphic\Ghost_Front.png').convert(),
            'back': pygame.image.load('graphic\Ghost_Back.png').convert(),
            'left': pygame.image.load('graphic\Ghost_Left.png').convert(),
            'right': pygame.image.load('graphic\Ghost_Right.png').convert()
        }

        for key in ghost_images:
            ghost_images[key].set_colorkey(WHITE)

        return ghost_images

    except pygame.error as e:
        print(f"Error loading images: {e}")
        return None

# Load player image
def load_player_image():
    try:
        current_dir = os.getcwd()
        parent_dir = os.path.dirname(current_dir)
        player_path = 'graphic\Standing_front.png'
        print(f"Looking for player image at: {player_path}")
        return pygame.image.load(player_path)
    except pygame.error as e:
        print(f"Error loading player image: {e}")
        return None

# Function to call login API and get the token
def login(username, password):
    try:
        response = requests.post(f'{API_URL}/login', json={'username': username, 'password': password})
        if response.status_code == 200:
            return response.json()['token']
        else:
            print(f"Login failed: {response.status_code}", response.json())
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return None

# Function to get player data
def get_player_data(token):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{API_URL}/get_player', headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting player data: {response.status_code}", response.json())
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return None

# Function to get the game state
def get_game_state(token, screen_width, screen_height):
    #try:
        headers = {'Authorization': f'Bearer {token}'}
        data = {'screen_width': screen_width, 'screen_height': screen_height}
        response = requests.post(f'{API_URL}/game_state', json=data, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting game state: {response.status_code}")
            return None
    #except requests.exceptions.RequestException as e:
       # print(f"Connection error: {e}")
       # return None

# Draw a bot relative to the player
def draw_bot(screen, bot, player_x, player_y, ghost_images):
    bot_x = bot.get('x', 0)
    bot_y = bot.get('y', 0)
    direction = bot.get('direction', 'front').lower()

    # המיקום במסך הוא:
    bot_location_x = (bot_x - player_x) + (SCREEN_WIDTH // 2)
    bot_location_y = (bot_y - player_y) + (SCREEN_HEIGHT // 2)

    if direction in ('up', 'back'):
        ghost_img = ghost_images['back']
    elif direction in ('down', 'front'):
        ghost_img = ghost_images['front']
    elif direction == 'left':
        ghost_img = ghost_images['left']
    elif direction == 'right':
        ghost_img = ghost_images['right']
    else:
        ghost_img = ghost_images['front']

    img_rect = ghost_img.get_rect(center=(bot_location_x, bot_location_y))
    screen.blit(ghost_img, img_rect)

# Draw player at center
def draw_player(screen, player_image):
    # השחקן תמיד באמצע המסך
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    player_rect = player_image.get_rect(center=(center_x, center_y))
    screen.blit(player_image, player_rect)

# Main visualization function
def main():
    global TOKEN
    ghost_images = load_images()
    player_image = load_player_image()
    if not ghost_images or not player_image:
        print("Failed to load required images.")
        return

    username = '2212'
    password = '2212'
    token = login(username, password)
    TOKEN = token
    if not token:
        print("Login failed, exiting...")
        return

    print("Login successful!")

    clock = pygame.time.Clock()
    running = True

    inventory_icon, mini_map_icon, exit_icon, chat_icon, current_holding, money_icon = create_icons()

    enter_inventory_data_to_json()
    while running:
        screen.fill(BACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        game_state = get_game_state(token, SCREEN_WIDTH, SCREEN_HEIGHT)
        player_data = get_player_data(token)

        if player_data:
            player_x = player_data.get('position_x', SCREEN_WIDTH // 2)
            player_y = player_data.get('position_y', SCREEN_HEIGHT // 2)

            # Draw bots relative to player
            if game_state and 'bots' in game_state:
                for bot in game_state['bots']:
                    draw_bot(screen, bot, player_x, player_y, ghost_images)

            # Draw player in center
            draw_player(screen, player_image)

        # UI Text
        status_text = font.render("Bot Visualization - Press ESC to exit", True, WHITE)
        screen.blit(status_text, (10, 10))

        if not put_icons_on_screen(screen, inventory_icon, mini_map_icon, exit_icon, chat_icon, current_holding,money_icon, event):
            running = False
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
