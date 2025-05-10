import pygame
import requests
import sys
import time
import os
import buttons
import json

# Initialize Pygame
pygame.init()

# Files:
INVENTORY_ICON = "Inventory_Icon.png"
EXIT_ICON = "Exit_Icon.png"
CHAT_ICON = "Chat_Icon.png"
MINI_MAP_ICON = "Map_Icon.png"
MONEY_ICON = "Money_Show.png"
NOT_OPEN_INVENTORY = r"Not_Open_Inventory.png"
FULL_INVENTORY_ITEMS = r"Full_Inventory_Items.png"
FULL_INVENTORY_SHOP = r"Full_Inventory_Shop.png"
FULL_HP_BAR = "Hp_Bar.png"
CHAT_WINDOW_LAYER_1 = "Chat_First_Layer.png"
CHAT_WINDOW_LAYER_2 = "Chat_Second_Layer.png"
CURRENT_HOLDING = "Current_Holding.png"
MINI_BUTTON_PRESSED = "Mini_Button_Pressed.png"
MINI_BUTTON_NOT_PRESSED = "Mini_Button_Not_Pressed.png"
DELETE_BUTTON = "Delete_Button.png"

# Constants for screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
window_height = 720
window_width = 1280
FPS = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
BACK = (182,212,137)
MONEY_TEXT = (129,69,37)

# Flags:
INVENTORY_OPEN_ITEMS = 0 #BOOLEAN OF NUMBERS- odd=full_inventory, even=not full inventory
INVENTORY_OPEN_SHOP = 0 #BOOLEAN OF NUMBERS- odd=full_inventory, even=not full inventory
CHAT_OPEN = 0 #BOOLEAN OF NUMBERS- odd=open, even=close
CLICKED = False

# Your API URL
API_URL = 'http://127.0.0.1:5000'
TOKEN = ""

WORLD_WIDTH  = SCREEN_WIDTH * 40
WORLD_HEIGHT = SCREEN_HEIGHT * 40

auto_walk = False
auto_stage = 0   # 0=למעלה, 1=ימינה, 2=למטה, 3=שמאלה
auto_last_move_time = 0
AUTO_DELAY = 0.05  # השהייה בין צעדים (שניות)

# Pygame screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bot Visualization')

# Font for screening text
font = pygame.font.SysFont('Arial', 16)

def create_icons():
    # inventory icon:
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'graphic'))
    inventory_image = pygame.image.load(os.path.join(path, INVENTORY_ICON)).convert()
    inventory_image.set_colorkey(WHITE)
    inventory_icon = buttons.Button(370, 30, inventory_image)

    # mini map frame:
    mini_map_image = pygame.image.load(os.path.join(path,MINI_MAP_ICON)).convert()
    mini_map_image.set_colorkey(WHITE)
    mini_map_icon = buttons.Button(30, 10, mini_map_image)

    # exit icon:
    exit_image = pygame.image.load(os.path.join(path,EXIT_ICON)).convert()
    exit_image.set_colorkey(WHITE)
    exit_icon = buttons.Button(270, 30, exit_image)

    # chat icon:
    chat_image = pygame.image.load(os.path.join(path,CHAT_ICON)).convert()
    chat_image.set_colorkey(WHITE)
    chat_icon = buttons.Button(470, 30, chat_image)

    # holding icon:
    current_holding_image = pygame.image.load(os.path.join(path,CURRENT_HOLDING)).convert()
    current_holding_image .set_colorkey(WHITE)
    current_holding = buttons.Button(150, 570, current_holding_image)

    # money icon:
    money_image = pygame.image.load(os.path.join(path,MONEY_ICON)).convert()
    money_image.set_colorkey(WHITE)
    money_icon = buttons.Button(1110, 654, money_image)

    return inventory_icon,mini_map_icon,exit_icon,chat_icon,current_holding, money_icon


def put_icons_on_screen(screen,inventory_icon, mini_map_icon, exit_icon, chat_icon,current_holding,money_icon,event):
    """
    prints on the screen the icons, the mini map frame
    """
    global INVENTORY_OPEN_ITEMS
    global INVENTORY_OPEN_SHOP
    global CHAT_OPEN
    global CLICKED

    if exit_icon.draw(screen):
        return False

    if chat_icon.draw(screen):
        CHAT_OPEN += 1

    if CHAT_OPEN % 2 == 1:
        open_chat(screen)

    if inventory_icon.draw(screen):
        INVENTORY_OPEN_ITEMS += 1
        INVENTORY_OPEN_SHOP = 0

    money_icon.draw(screen)
    money = get_coins()
    font = pygame.font.Font(None, 35)
    amount = font.render( str(money), True, MONEY_TEXT)
    screen.blit(amount, (1168, 667))

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
        open_full_inventory_items(screen,event)

    elif INVENTORY_OPEN_SHOP % 2 == 1:
        open_full_inventory_shop(screen,event)

    elif INVENTORY_OPEN_ITEMS % 2 == 0 and INVENTORY_OPEN_SHOP % 2 == 0:
        open_not_full_inventory(screen,event)

    if event.type == pygame.MOUSEBUTTONUP:
        CLICKED = False

    mini_map_icon.draw(screen)
    current_holding.draw(screen)
    print_current_holding(screen,event)
    return True


##########################################################################################################
# open windows:

def open_chat(screen):
    """
    opens the chat window
    """
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'graphic'))
    open_chat_first_layer_image = pygame.image.load(os.path.join(path,CHAT_WINDOW_LAYER_1)).convert_alpha()
    open_chat_first_layer_image.set_colorkey(WHITE)
    open_chat_first_layer_image.set_alpha(180)
    chat_first_layer = buttons.Button(810, 30, open_chat_first_layer_image)
    chat_first_layer.draw(screen)

    open_chat_second_layer_image = pygame.image.load(os.path.join(path,CHAT_WINDOW_LAYER_2)).convert()
    open_chat_second_layer_image.set_colorkey(WHITE)
    chat_second_layer = buttons.Button(810, 30, open_chat_second_layer_image)
    chat_second_layer.draw(screen)


def open_full_inventory_items(screen, event):
    """
    draw full inventory open - items
    """
    global CLICKED
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'graphic'))
    open_full_inventory_image = pygame.image.load(os.path.join(path,FULL_INVENTORY_ITEMS)).convert()
    open_full_inventory_image.set_colorkey(WHITE)
    full_inventory = buttons.Button(350, 119, open_full_inventory_image)
    full_inventory.draw(screen)

    hp_bar_image = pygame.image.load(os.path.join(path,FULL_HP_BAR)).convert()
    hp_bar_image.set_colorkey(WHITE)
    hp_bar_icon = buttons.Button(640, 170, hp_bar_image)
    hp_bar_icon.draw(screen)
    draw_full_inventory_hp_bar(screen)

    print_full_inventory(screen,event)
    print_mini_buttons(screen,event)
    print_delete_buttons(screen,event)


def open_full_inventory_shop(screen,event):
    """
    draw full inventory open - shop
    """
    global CLICKED
    money = get_coins()
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'graphic'))
    open_full_inventory_image = pygame.image.load(os.path.join(path,FULL_INVENTORY_SHOP)).convert()
    open_full_inventory_image.set_colorkey(WHITE)
    full_inventory = buttons.Button(350, 119, open_full_inventory_image)
    full_inventory.draw(screen)

    hp_bar_image = pygame.image.load(os.path.join(path,FULL_HP_BAR)).convert()
    hp_bar_image.set_colorkey(WHITE)
    hp_bar_icon = buttons.Button(640, 170, hp_bar_image)
    hp_bar_icon.draw(screen)
    draw_full_inventory_hp_bar(screen)

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

    print_full_inventory(screen,event)
    print_mini_buttons(screen,event)
    print_delete_buttons(screen,event)


def open_not_full_inventory(screen,event):
    """
    draw not full inventory
    """
    global CLICKED
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'graphic'))
    inventory_not_open_image = pygame.image.load(os.path.join(path,NOT_OPEN_INVENTORY)).convert()
    inventory_not_open_image.set_colorkey(WHITE)
    inventory_not_open = buttons.Button(350, 570, inventory_not_open_image)
    inventory_not_open.draw(screen)

    # hp bar:
    hp_bar_image = pygame.image.load(os.path.join(path,FULL_HP_BAR)).convert()
    hp_bar_image.set_colorkey(WHITE)
    hp_bar_icon = buttons.Button(350, 520, hp_bar_image)
    hp_bar_icon.draw(screen)
    draw_not_full_inventory_hp_bar(screen)
    print_not_full_inventory(screen,event)


##########################################################################################################
# print items and buttons:

def print_not_full_inventory(screen,event):
    """
    prints in the small inventory the items, the anoumt
    """
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'inventory'))
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
        image = pygame.image.load(os.path.join(path,image_place)).convert()
        image.set_colorkey(WHITE)
        cell = buttons.Button(x, y, image)
        if cell.draw(screen):
            current_holding_change(i)
        # draw the amount:
        if data_items["items"][item]["stackable"]:
            amount = font.render(str(quantity), True, WHITE)
            screen.blit(amount, (x+77,y+3))


def print_full_inventory(screen,event):
    """
    prints in the full inventory the items
    :return:
    """
    global CLICKED
    if event.type == pygame.MOUSEBUTTONUP:
        CLICKED = False
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'inventory'))
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
        image = pygame.image.load(os.path.join(path,image_place)).convert()
        image.set_colorkey(WHITE)
        cellp = buttons.Button(x, y, image)
        cellp.draw(screen)

        # draw the amount:
        if data_items["items"][item]["stackable"]:
            amount = font.render(str(quantity), True, WHITE)
            screen.blit(amount, (x+77,y+3))


def print_current_holding(screen,event):
    """
    drawing the current holding
    """
    global CLICKED
    if event.type == pygame.MOUSEBUTTONUP:
        CLICKED = False
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'inventory'))
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
    image = pygame.image.load(os.path.join(path,image_place)).convert()
    image.set_colorkey(WHITE)
    cell = buttons.Button(x, y, image)
    if cell.draw(screen) and not CLICKED:
        CLICKED = True
        if item not in ["0", "1", "2", "3", "4", "5", "12", "13", "14"]:
            send_use_object(item)
        if item in ["6", "7", "8", "10", "11"]:
            delete_item_from_json(item,  data_cells["cells"]["19"]["cell"])

    if data_items["items"][item]["stackable"]:
        amount = font.render(str(quantity), True, WHITE)
        screen.blit(amount, (x + 77, y + 3))


def print_mini_buttons(screen,event):
    """
    draws the mini button when you open the full inventory
    """
    global CLICKED
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)

    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'graphic'))
    for i in range(1, 19):

        cell = data_cells["cells"][str(i)]
        x = cell["topleft_x"]
        y = cell["topleft_y"]
        mini_button = cell["mini_button_pressed?"]
        # draw the mini button:
        if mini_button:
            button_image = pygame.image.load(os.path.join(path,MINI_BUTTON_PRESSED)).convert()
            if 1 <= i <= 6:
                button = buttons.Button(x, y + 103, button_image)
            else:
                button = buttons.Button(x, y + 85, button_image)
            button.draw(screen)
        else:

            button_image = pygame.image.load(os.path.join(path,MINI_BUTTON_NOT_PRESSED)).convert()
            if 1 <= i <= 6:
                button = buttons.Button(x, y + 103, button_image)
            else:
                button = buttons.Button(x, y + 85, button_image)
            if button.draw(screen) and not CLICKED:
                CLICKED = True
                mini_button_change(i)
                bool, cell1, cell2 = both_mini_button_pressed()
                if bool:
                    switch_items_in_inventory(cell1, cell2)


def print_delete_buttons(screen,event):
    """
        draws the mini button when you open the full inventory
        """
    global CLICKED
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'graphic'))
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)

    for i in range(1, 19):

        cell = data_cells["cells"][str(i)]
        x = cell["topleft_x"]
        y = cell["topleft_y"]
        item = cell["item"]

        button_image = pygame.image.load(os.path.join(path,DELETE_BUTTON)).convert()
        if 1 <= i <= 6:
            button = buttons.Button(x, y + 83, button_image)
        else:
            button = buttons.Button(x, y + 65, button_image)
        if button.draw(screen) and not CLICKED:
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

    # delete the info of both in the sever:
    if item1 != "0":
        delete_item_inventory(item1,cell_num1, quantity1)
    if item2 != "0":
        delete_item_inventory(item2, cell_num2, quantity2)

    #switch in the server:
    if item2 != "0":
        add_item_inventory(item2, cell_num1, True, quantity2)
    if item1 != "0":
        add_item_inventory(item1,cell_num2,True,quantity1)


    for cell in data_cells["cells"].values():
        cell["mini_button_pressed?"] = False

    with open("inventory.json", "w") as file_cells:
        json.dump(data_cells, file_cells, indent=4)

    print(data_cells)


##########################################################################################################
# HP bar:

def draw_not_full_inventory_hp_bar(screen):
    """
    print the white area of the hp bar when the inventory is not full
    """
    hp = get_health()
    # משהו שמבקש את הHP של השחקן מהשרת
    lack = 100 - hp
    width = int((379 * lack)/100)
    height = 22
    pygame.draw.rect(screen, WHITE, (736-width, 528, width, height))


def draw_full_inventory_hp_bar(screen):
    """
    print the white area of the hp bar when the inventory is full
    """
    hp = get_health()
    lack = 100 - hp
    width = int((379 * lack) / 100)
    height = 22
    pygame.draw.rect(screen, WHITE, (1026 - width, 178, width, height))


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
                data_cells["cells"][str(i)]["item"] = str(id)
                data_cells["cells"][str(i)]["quantity"] = int(quantity)
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


def check_obj():
    """
    check if there are any objects the player can take on the map
    :return:
    """
    game_state = get_game_state(TOKEN,SCREEN_WIDTH, SCREEN_HEIGHT)
    if game_state and 'objects' in game_state:
        objects = game_state['objects']
        for obj in objects:
            pass
             # print(f"אובייקט: {obj['name']} במיקום ({obj['x']}, {obj['y']}) עם קובץ {obj['file']}")


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


def add_item_inventory(object_id, slot_index, has_space, amount=1):
    """
    שולח בקשה לשרת להוספת פריט לאינבנטורי
    :param object_id: מזהה פנימי של הפריט (יומר לשם)
    :param slot_index: מספר הסלוט באינבנטורי
    :param has_space: האם יש מקום באינבנטורי
    :param amount: כמות להוסיף (ברירת מחדל: 1)
    :return: תשובת השרת (dict) או None במקרה של כשל
    """
    object_name = id_to_name(object_id)
    if object_name is None:
        print(f"❌ Invalid object_id: {object_id}")
        return None

    url = f"{API_URL}/add-to-inventory"
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }

    data = {
        "object_name": object_name,
        "slot_index": slot_index,
        "has_space_in_inventory": has_space,
        "amount": amount
    }

    print("📤 Sending:", data)
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Added to inventory: {result.get('message')}")
                return result
            else:
                print(f"ℹ️ Not added: {result.get('message')}")
        elif response.status_code == 404:
            print("❌ Object not found on the map.")
        elif response.status_code == 400:
            print("❌ Bad request: Missing or invalid data.", response.text)
        elif response.status_code == 401:
            print("❌ Unauthorized: Invalid or missing token.")
        else:
            print(f"❌ Unexpected error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error connecting to server: {e}")

    return None


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


def delete_item_inventory(item_name, slot_index, amount=1, server_url="http://localhost:5000"):
    """
    שולחת בקשה לשרת להסרת פריט מהאינבנטורי לפי שם, מיקום וסכום.

    :param item_name: שם הפריט (או מזהה שלו אם יש צורך בתרגום)
    :param slot_index: אינדקס הסלוט ממנו להסיר
    :param amount: כמות להסרה (ברירת מחדל: 1)
    :param server_url: כתובת השרת
    """
    url = f"{server_url}/remove_from_inventory"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "item_name": id_to_name(item_name),  # אם item_name כבר שם, הסירי את הקריאה הזו
        "slot_index": slot_index,
        "amount": amount
    }

    print("sent to server:", url, payload, headers)
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"✅ Success: {response.json().get('message')}")
        else:
            print(f"❌ Error {response.status_code}: {response.json().get('error')}")
    except Exception as e:
        print(f"⚠️ Request failed: {e}")



##########################################################################################################
# client not inventory:


def send_item_drop_to_server(items, token):
    print("send start")
    headers = {"Authorization": f"Bearer {token}"}
    seen = set()  # לשמירת פריטים שנשלחו

    for item in items:
        if 'file' in item:
            key = (item['file'], item['x'], item['y'])
            if key in seen:
                continue  # כבר נשלח
            seen.add(key)

            amount = 100 if item['file'].lower() == 'money' else 1
            data = {
                "name": item['file'],
                "x": item['x'],
                "y": item['y'],
                "amount": amount
            }
            print(data)
            try:
                response = requests.post(f"{API_URL}/drop_item_on_map", json=data, headers=headers)
                if response.status_code != 200:
                    print(f"Failed to drop item {item['file']} on map: {response.json()}")
            except Exception as e:
                print(f"Error dropping {item['file']} on map:", e)


def check_click_not_on_ui(x,y):
    """
    check if the player clicked on the ui or have an item you cant attack with
    """
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)
    cell = data_cells["cells"]["19"]["cell"]  # cell - number of the cell that the current holding holds
    held_cell = data_cells["cells"][cell]
    item = held_cell["item"]

    # ui buttons:
    if 271 < x < 349 or 374 < x < 450 or 473 < x < 550 and 34 < y < 106:
        return True, None
    # mini map:
    if 28 < x < 240 and 34 < y < 236:
        return True, None
    # current holding:
    if 152 < x < 283 and 572 < y < 701:
        return True, None
    # inventory:
    if 351 < x < 1032 and 570 < y < 698:
        return True, None
    # hp bar:
    if 351 < x < 745 and 522 < y < 555:
        return True, None
    # money:
    if 1110 < x < 1262 and 661 < y < 700:
        return True, None
    if item not in ["1", "2", "3", "4", "5"]:
        return True, None
    print("hayo")

    return False, item


def handle_auto_movement(token, player_data):
    """
    זז לאורך גבולות המפה בסדר מחזורי (ימינה, למעלה, שמאלה, למטה)
    ומחליף כיוון אוטומטית כשהגיע לגבול.
    """
    global auto_stage, auto_last_move_time

    now = time.time()
    if now - auto_last_move_time < AUTO_DELAY:
        return None
    auto_last_move_time = now

    px = player_data['position_x']
    py = player_data['position_y']

    for _ in range(4):  # ננסה עד שנמצא כיוון חוקי
        direction = None
        print(f"[AUTO] Stage: {auto_stage}, Pos: ({px}, {py})")

        if auto_stage == 0:  # ימינה
            if px < WORLD_WIDTH - SCREEN_WIDTH // 2:
                direction = 'd'
            else:
                auto_stage = 1
                continue
        elif auto_stage == 1:  # למעלה
            if py > SCREEN_HEIGHT // 2:
                direction = 'w'
            else:
                auto_stage = 2
                continue
        elif auto_stage == 2:  # שמאלה
            if px > SCREEN_WIDTH // 2 + 5:
                direction = 'a'
            else:
                auto_stage = 3
                continue
        elif auto_stage == 3:  # למטה
            if py < WORLD_HEIGHT - SCREEN_HEIGHT // 2 - 5:
                direction = 's'
            else:
                auto_stage = 0
                continue

        if direction:
            print(f"[AUTO] Moving {direction}")
            headers = {'Authorization': f'Bearer {token}'}
            data = {
                'direction': direction,
                'screen_width': SCREEN_WIDTH,
                'screen_height': SCREEN_HEIGHT
            }
            try:
                resp = requests.post(f'{API_URL}/movement', json=data, headers=headers)
                if resp.status_code == 200:
                    return resp.json()
                else:
                    print(f"[AUTO] Movement failed: {resp.status_code}")
            except Exception as e:
                print(f"[AUTO] Request error: {e}")
            break

    return None


def load_images():
    try:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'graphic', 'bot'))
        print(f"Looking for images in: {base_path}")
        ghost_images = {
            'front': pygame.image.load(os.path.join(base_path, 'Ghost_Front.png')).convert(),
            'back': pygame.image.load(os.path.join(base_path, 'Ghost_Back.png')).convert(),
            'left': pygame.image.load(os.path.join(base_path, 'Ghost_Left.png')).convert(),
            'right': pygame.image.load(os.path.join(base_path, 'Ghost_Right.png')).convert()
        }
        for key in ghost_images:
            ghost_images[key].set_colorkey((255, 255, 255))
        return ghost_images
    except pygame.error as e:
        print(f"Error loading bot images: {e}")
        return None

# Load player image
def load_player_image():
    try:
        player_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'graphic'))
         #print(f"Looking for player image at: {player_path}")
        player_image = pygame.image.load(os.path.join(player_path, 'Standing_front.png')).convert()
        player_image.set_colorkey((0, 0, 0))
        return player_image
    except pygame.error as e:
        print(f"Error loading player image: {e}")
        return None


# Draw an object relative to the player's position
def draw_object(screen, obj, player_x, player_y, object_images):
    obj_x = obj.get('x', 0)
    obj_y = obj.get('y', 0)
    file_name = obj.get('file')

    object_location_x = (obj_x - player_x) + (SCREEN_WIDTH // 2)
    object_location_y = (obj_y - player_y) + (SCREEN_HEIGHT // 2)

    if file_name and file_name.lower().endswith('.png') and file_name.lower() in object_images:
        obj_img = object_images[file_name.lower()]
        obj_rect = obj_img.get_rect(center=(object_location_x, object_location_y))
        screen.blit(obj_img, obj_rect)

# Load all object images from the graphic folder
def load_object_images():
    try:
        object_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'graphic'))
        print(f"Looking for object images in: {object_path}")
        object_images = {}

        for filename in os.listdir(object_path):
            if filename.endswith('.png'):
                name = filename.lower()
                full_path = os.path.join(object_path, filename)
                image = pygame.image.load(full_path).convert()
                image.set_colorkey((255, 255, 255))
                object_images[name] = image

        return object_images

    except pygame.error as e:
        print(f"Error loading object images: {e}")
        return {}

# Handle player movement and request updated game state
def handle_player_movement(token, screen_width, screen_height):
    keys = pygame.key.get_pressed()
    direction = None

    if keys[pygame.K_w]:
        direction = 'w'
    elif keys[pygame.K_a]:
        direction = 'a'
    elif keys[pygame.K_s]:
        direction = 's'
    elif keys[pygame.K_d]:
        direction = 'd'

    if direction:
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'direction': direction,
            'screen_width': screen_width,
            'screen_height': screen_height
        }
        try:
            response = requests.post(f'{API_URL}/movement', json=data, headers=headers)
            # print("movement:", response.json())
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Movement error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error sending movement: {e}")
    return None

# Get current player data
def get_player_data(token):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{API_URL}/get_player', headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching player data: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection error fetching player data: {e}")
        return None

# Get full game state
def get_game_state(token, screen_width, screen_height):
    start = time.time()
    try:
        headers = {'Authorization': f'Bearer {token}'}
        data = {'screen_width': screen_width, 'screen_height': screen_height}
        response = requests.post(f'{API_URL}/game_state', json=data, headers=headers)
        if response.status_code == 200:
            game_state_data = response.json()
            if 'bots' in game_state_data:
                pass
                # print(f"[DEBUG] Received {len(game_state_data['bots'])} bots from server.")
            # print(f"get_game_state client: {time.time() - start}")
            return game_state_data
        else:
            print(f"Error fetching game state: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Connection error fetching game state: {e}")
    return None

# Draw a bot relative to the player
def draw_bot(screen, bot, player_x, player_y, ghost_images):
    # print(f"[DEBUG] Drawing bot: {bot}")
    bot_x = bot.get('x', 0)
    bot_y = bot.get('y', 0)
    direction = bot.get('direction', 'front').lower()

    bot_location_x = (bot_x - player_x) + (SCREEN_WIDTH // 2)
    bot_location_y = (bot_y - player_y) + (SCREEN_HEIGHT // 2)

    if direction in ('up', 'back'):
        ghost_img = ghost_images.get('back')
        # print(f"[DEBUG] Bot direction: {direction}, using image: back")
    elif direction in ('down', 'front'):
        ghost_img = ghost_images.get('front')
        # print(f"[DEBUG] Bot direction: {direction}, using image: front")
    elif direction == 'left':
        ghost_img = ghost_images.get('left')
        # print(f"[DEBUG] Bot direction: {direction}, using image: left")
    elif direction == 'right':
        ghost_img = ghost_images.get('right')
        # print(f"[DEBUG] Bot direction: {direction}, using image: right")
    else:
        ghost_img = ghost_images.get('front')
        # print(f"[DEBUG] Unknown bot direction: {direction}, using image: front")

    if ghost_img:
        img_rect = ghost_img.get_rect(center=(bot_location_x, bot_location_y))
        screen.blit(ghost_img, img_rect)
    else:
        print(f"[WARNING] No image found for bot direction: {direction}")

def send_attack_request(token, x, y, weapon_type, server_url='http://127.0.0.1:5000/attack'):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = {
        'x': x,
        'y': y,
        'weapon_type': weapon_type  # לדוגמה: 'Stone_Sword', 'Wood_Wand' וכו'
    }

    try:
        response = requests.post(server_url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            print("Attack result:", result['message'])
            return result
        else:
            print("Attack failed:", response.status_code, response.text)
    except Exception as e:
        print("Error sending attack:", e)

# Draw the player in the center
def draw_player(screen, player_image):
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    player_rect = player_image.get_rect(center=(center_x, center_y))
    screen.blit(player_image, player_rect)


def send_item_drop_to_server(items, token):
    print("send start")
    headers = {"Authorization": f"Bearer {token}"}
    seen = set()  # לשמירת פריטים שנשלחו

    for item in items:
        if 'file' in item:
            key = (item['file'], item['x'], item['y'])
            if key in seen:
                continue  # כבר נשלח
            seen.add(key)

            amount = 100 if item['file'].lower() == 'money' else 1
            data = {
                "name": item['file'],
                "x": item['x'],
                "y": item['y'],
                "amount": amount
            }
            print(data)
            try:
                response = requests.post(f"{API_URL}/drop_item_on_map", json=data, headers=headers)
                if response.status_code != 200:
                    print(f"Failed to drop item {item['file']} on map: {response.json()}")
            except Exception as e:
                print(f"Error dropping {item['file']} on map:", e)



def main(token):
    global TOKEN
    TOKEN = token
    ghost_images = load_images()
    player_image = load_player_image()
    object_images = load_object_images()

    if not ghost_images:
        print("Error: Bot images were not loaded.")
        return
    if not player_image:
        print("Error: Player image was not loaded.")
        return
    if not object_images:
        print("Error: Object images were not loaded.")
        return

    clock = pygame.time.Clock()
    running = True
    dropped_items = []
    player_data = get_player_data(token)

    inventory_icon, mini_map_icon, exit_icon, chat_icon, current_holding, money_icon = create_icons()
    enter_inventory_data_to_json()

    while running:
        screen.fill(BACK)
        start = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    global auto_walk
                    auto_walk = not auto_walk
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                bad_attack, weapon = check_click_not_on_ui(mouse_x, mouse_y)
                if not bad_attack:
                    click_world_x = mouse_x + player_data['position_x'] - SCREEN_WIDTH // 2
                    click_world_y = mouse_y + player_data['position_y'] - SCREEN_HEIGHT // 2

                    result = send_attack_request(token, click_world_x, click_world_y, weapon)
                    if result and "drops" in result:
                        items = result["drops"]
                        if len(items) >= 1:
                            dropped_items.append({
                                "file": items[0],
                                "x": click_world_x,
                                "y": click_world_y
                            })
                        if len(items) >= 2:
                            dropped_items.append({
                                "file": items[1],
                                "x": click_world_x + 100,
                                "y": click_world_y
                            })
                        #print("dropped_items", dropped_items)
                    print("attacked")

        if auto_walk:
            game_state = handle_auto_movement(token, player_data)
        else:
            game_state = handle_player_movement(token, SCREEN_WIDTH, SCREEN_HEIGHT)
        if not game_state:
            game_state = get_game_state(token, SCREEN_WIDTH, SCREEN_HEIGHT)
        check_obj()
        # עדכן את player_data מתוך game_state אם יש
        if game_state and 'player' in game_state:
            player_data = game_state['player']
        else:
            player_data = get_player_data(token)

        # בדיקה אם השחקן מת
        if player_data and player_data.get('health', 100) <= 0:
            # print("[INFO] Player is dead. Attempting to respawn...")
            try:
                headers = {'Authorization': f'Bearer {token}'}
                respawn_response = requests.post(f'{API_URL}/respawn', headers=headers)
                if respawn_response.status_code == 200:
                    # print("[INFO] Player respawned successfully.")
                    player_data = get_player_data(token)
                else:
                    print(f"[ERROR] Respawn failed: {respawn_response.status_code} - {respawn_response.text}")
            except requests.exceptions.RequestException as e:
                 print(f"[ERROR] Connection error while respawning: {e}")

        # ציור


        if player_data:
            player_x = player_data.get('position_x', SCREEN_WIDTH // 2)
            player_y = player_data.get('position_y', SCREEN_HEIGHT // 2)
            # print(f"[DEBUG] Player position: {player_x}, {player_y}")

            if game_state and 'objects' in game_state:
                for obj in game_state['objects']:
                    draw_object(screen, obj, player_x, player_y, object_images)
            # print("dropped_items",dropped_items)

            for item in dropped_items:
                if item['file'].lower() == 'money':
                    continue
                try:
                    filename = f"{os.path.splitext(item['file'])[0]}_Inventory.png"
                    image = pygame.image.load(os.path.join("inventory", filename)).convert_alpha()
                    image.set_colorkey((255, 255, 255))
                    screen.blit(image, (
                        item["x"] - player_x + SCREEN_WIDTH // 2,
                        item["y"] - player_y + SCREEN_HEIGHT // 2
                    ))
                    send_item_drop_to_server(dropped_items, token)
                except FileNotFoundError:
                    print(f"Image file not found: {filename}")

            if game_state and 'bots' in game_state:
                for bot in game_state['bots']:
                    draw_bot(screen, bot, player_x, player_y, ghost_images)

            draw_player(screen, player_image)
            if not put_icons_on_screen(screen, inventory_icon, mini_map_icon, exit_icon, chat_icon, current_holding,money_icon, event):
                running = False
        status_text = font.render("Bot Visualization - Press ESC to exit", True, WHITE)
        screen.blit(status_text, (10, 10))
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()
