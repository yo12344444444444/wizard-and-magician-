import pygame
import buttons
import json

INVENTORY_ICON = "graphic\Inventory_Icon.png"
EXIT_ICON = "graphic\Exit_Icon.png"
CHAT_ICON = "graphic\Chat_Icon.png"
MINI_MAP_ICON = "graphic\Map_Icon.png"
NOT_OPEN_INVENTORY = r"graphic\Not_Open_Inventory.png"
FULL_INVENTORY = r"graphic\Full_Inventory.png"
FULL_HP_BAR = "graphic\Hp_Bar.png"
CHAT_WINDOW_LAYER_1 = "graphic\Chat_First_Layer.png"
CHAT_WINDOW_LAYER_2 = "graphic\Chat_Second_Layer.png"
CURRENT_HOLDING = "graphic\Current_Holding.png"
MINI_BUTTON_PRESSED = "graphic\Mini_Button_Pressed.png"
MINI_BUTTON_NOT_PRESSED = "graphic\Mini_Button_Not_Pressed.png"
WHITE = (255, 255, 255)
BACK = (182, 212, 137)

frames_per_second = 30
window_height = 720
window_width = 1280

INVENTORY_OPEN = 0  # BOOLEAN OF NUMBERS- odd=full_inventory, even=not full inventory
CHAT_OPEN = 0  # BOOLEAN OF NUMBERS- odd=open, even=close
display = pygame.display.set_mode((window_width, window_height))
display.fill(BACK)

reset_mini_buttons = False  # דגל לדחיית איפוס הכפתורים


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


def open_full_inventory(display):
    """
    draw full inventory open - items
    """
    open_full_inventory_image = pygame.image.load(FULL_INVENTORY).convert()
    open_full_inventory_image.set_colorkey(WHITE)
    full_inventory = buttons.Button(350, 119, open_full_inventory_image)
    full_inventory.draw(display)

    hp_bar_image = pygame.image.load(FULL_HP_BAR).convert()
    hp_bar_image.set_colorkey(WHITE)
    hp_bar_icon = buttons.Button(640, 170, hp_bar_image)
    hp_bar_icon.draw(display)

    print_full_inventory(display)
    draw_mini_buttons(display)


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

    print_not_full_inventory(display)


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
        json.dump(data_cells, file_cells, indent=4)


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
    for i in range(1, 19):
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

    global reset_mini_buttons
    reset_mini_buttons = True  # סמון לדחיית איפוס הכפתורים

    with open("inventory.json", "w") as file_cells:
        json.dump(data_cells, file_cells, indent=4)


def print_not_full_inventory(display):
    """
    prints in the small inventory the items, the amount, and the mini button
    """
    font = pygame.font.Font(None, 25)
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)
    with open("items.json", "r") as file_items:
        data_items = json.load(file_items)
    for i in range(1, 7):

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
            display.blit(amount, (x + 77, y + 3))


def print_full_inventory(display):
    """
    prints in the full inventory the items
    """
    font = pygame.font.Font(None, 25)
    with open("inventory.json", "r") as file_cells:
        data_cells = json.load(file_cells)
    with open("items.json", "r") as file_items:
        data_items = json.load(file_items)
    for i in range(1, 19):

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
            display.blit(amount, (x + 77, y + 3))


def draw_current_holding(display):
    """
    drawing the current holding
    """
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
    cell.draw(display)

    if data_items["items"][item]["stackable"]:
        amount = font.render(str(quantity), True, WHITE)
        display.blit(amount, (x + 77, y + 3))


def draw_mini_buttons(display):
    """
    draws the mini button when you open the full inventory
    """
    global reset_mini_buttons
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
            if button.draw(display):
                mini_button_change(i)
                bool, cell1, cell2 = both_mini_button_pressed()
                if bool:
                    switch_items_in_inventory(cell1, cell2)
                    reset_mini_buttons = False  # לאחר סוויץ' איפוס הכפתורים יתבצע אחרי דחייה.
                else:
                    reset_mini_buttons = True  # אם לא התבצע סוויץ', דוחה איפוס
                    # מחכים להבא, לא לאפס את הכפתורים כרגע
                if reset_mini_buttons:
                    with open("inventory.json", "r") as file_cells:
                        data_cells = json.load(file_cells)

                    for i in range(1, 19):
                        data_cells["cells"][str(i)]["mini_button_pressed?"] = False
                    with open("inventory.json", "w") as file_cells:
                        json.dump(data_cells, file_cells, indent=4)
                    reset_mini_buttons = False  #


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

    return inventory_icon,mini_map_icon,exit_icon,chat_icon,current_holding


def put_icons_on_screen(display,inventory_icon, mini_map_icon, exit_icon, chat_icon,current_holding):
    """
    prints on the screen the icons, the mini map frame
    """
    global INVENTORY_OPEN
    global CHAT_OPEN

    if inventory_icon.draw(display):
        INVENTORY_OPEN += 1
    if INVENTORY_OPEN % 2 == 1:
        open_full_inventory(display)
    if INVENTORY_OPEN % 2 == 0:
        open_not_full_inventory(display)
    if exit_icon.draw(display):
        return False
    if chat_icon.draw(display):
        CHAT_OPEN +=1
    if CHAT_OPEN % 2 == 1:
        open_chat()
    mini_map_icon.draw(display)
    current_holding.draw(display)
    draw_current_holding(display)
    return True

pygame.init()
inventory_icon, mini_map_icon, exit_icon, chat_icon,current_holding = create_icons()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    display.fill(BACK)
    if not put_icons_on_screen(display,inventory_icon, mini_map_icon, exit_icon, chat_icon,current_holding):
        running = False
    pygame.display.flip()
pygame.quit()