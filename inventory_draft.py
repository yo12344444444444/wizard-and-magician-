import pygame

INVENTORY_ICON = "graphic\Inventory_Icon.png"
EXIT_ICON = "graphic\Exit_Icon.png"
CHAT_ICON = "graphic\Chat_Icon.png"
MINI_MAP_ICON = "graphic\Map_Icon.png"
NOT_OPEN_INVENTORY = r"graphic\Not_Open_Inventory.png"
FULL_HP_BAR = "graphic\Hp_Bar.png"
WHITE = (255,255,255)
BACK = (182,212,137)


def put_icons_on_screen(screen):
    """
    prints on the screen the icons, the mini map frame and the not oen inventory
    without items
    """
    # inventory icon:
    inventory_icon = pygame.image.load(INVENTORY_ICON).convert()
    inventory_icon.set_colorkey(WHITE)

    # mini map frame:
    mini_map_icon = pygame.image.load(MINI_MAP_ICON).convert()
    mini_map_icon.set_colorkey(WHITE)

    # exit icon:
    exit_icon = pygame.image.load(EXIT_ICON).convert()
    exit_icon.set_colorkey(WHITE)

    # chat icon:
    chat_icon = pygame.image.load(CHAT_ICON).convert()
    chat_icon.set_colorkey(WHITE)

    # inventory not open:
    inventory_not_open = pygame.image.load(NOT_OPEN_INVENTORY).convert()
    inventory_not_open.set_colorkey(WHITE)

    #hp bar:
    hp_bar = pygame.image.load(FULL_HP_BAR).convert()
    hp_bar.set_colorkey(WHITE)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(BACK)
        screen.blit(mini_map_icon, (30, 10))
        screen.blit(exit_icon, (270, 30))
        screen.blit(inventory_icon, (370, 30))
        screen.blit(chat_icon, (470, 30))
        screen.blit(inventory_not_open, (300,650))
        screen.blit(hp_bar, (300, 600))
        # עדכון המסך
        pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("game")
    screen_width, screen_height = pygame.display.get_surface().get_size()
    put_icons_on_screen(screen)
    pygame.quit()

if __name__ == "__main__":
    main()