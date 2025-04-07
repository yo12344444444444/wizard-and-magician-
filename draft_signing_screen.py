import pygame

pygame.init()

# הגדרות מסך
screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Input Example")

# טוען תמונה ומגדיל לגודל המסך
image = pygame.image.load('screens\SigningScreen1.0.png')  # שים כאן את המיקום של התמונה
image = pygame.transform.scale(image, (screen_width, screen_height))

# צבעים וגופן
WHITE = (255, 255, 255)
font = pygame.font.Font(None, 70)

# משתנה לקלט מהמשתמש
user_text = ""
input_active = False  # האם מצב קלט פעיל?

running = True
while running:
    screen.blit(image, (0, 0))  # מצייר את התמונה ברקע

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # בדיקה אם המשתמש לחץ על האזור שבו מתחיל הקלט
            if 217 < x < 1105 and 227 < y < 305:
                input_active = True  # מפעיל את מצב הקלט

        elif input_active and event.type == pygame.KEYDOWN:  # קלט עובד רק אם input_active = True
            if event.key == pygame.K_BACKSPACE:
                user_text = user_text[:-1]
            else:
                user_text += event.unicode

    # מציג את הטקסט רק אם מצב הקלט פעיל
    if input_active:
        text_surface = font.render(user_text, True, WHITE)
        text_position = (490, 217)
        screen.blit(text_surface, text_position)

    pygame.display.flip()  # מרענן את המסך

pygame.quit()
