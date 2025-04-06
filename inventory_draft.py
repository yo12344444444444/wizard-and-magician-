import pygame

# אתחול Pygame
pygame.init()

# יצירת חלון
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("רקע לבן ואייקון")

# צבעים
WHITE = (255, 255, 255)

# טען את האייקון (תמונה כלשהי בפורמט PNG עם רקע שקוף)
# ודא שהקובץ נמצא באותה תיקייה או ציין נתיב מלא
icon = pygame.image.load("graphic\Inventory_Icon.jpg").convert_alpha()

# מיקום של האייקון
icon_x = 300
icon_y = 200

# לולאת המשחק
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # רקע לבן
    screen.fill(WHITE)

    # ציור האייקון במיקום שבחרת
    screen.blit(icon, (icon_x, icon_y))

    # עדכון המסך
    pygame.display.flip()

# סיום
pygame.quit()