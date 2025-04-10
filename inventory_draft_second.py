import pygame


class SmallButton():
    def __init__(self, x, y, image, normal_color, clicked_color):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.normal_color = normal_color  # צבע רגיל
        self.clicked_color = clicked_color  # צבע בלחיצה
        self.current_color = self.normal_color  # צבע התחלתי הוא רגיל

    def draw(self, display):
        action = False
        pos = pygame.mouse.get_pos()

        # בדיקת אם העכבר על הכפתור
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                # אם הכפתור נלחץ, שנה את הצבע והפעל את הפעולה
                self.clicked = True
                self.current_color = self.clicked_color
                action = True
            elif pygame.mouse.get_pressed()[0] == 0:
                # אם העכבר שוחרר, שנה חזרה לצבע הרגיל
                self.clicked = False


        # יצירת מלבן בגודל של הכפתור עם הצבע הנוכחי
        pygame.draw.rect(display, self.current_color, self.rect)

        # הצגת התמונה על הכפתור
        display.blit(self.image, (self.rect.x, self.rect.y))

        return action


# דוגמת שימוש:

pygame.init()

# יצירת מסך ופרטי הכפתור
window_width, window_height = 800, 600
display = pygame.display.set_mode((window_width, window_height))

# תמונה לכפתור
button_image = pygame.Surface((100, 50))  # כפתור בגודל 100x50
button_image.fill((0, 255, 0))  # צבע הכפתור (ירוק לדוגמה)

# יצירת כפתור קטן
small_button = SmallButton(350, 275, button_image, (0, 255, 0), (255, 0, 0))  # ירוק רגיל, אדום בלחיצה

# לולאת המשחק
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    display.fill((255, 255, 255))  # רקע לבן

    # Draw and check if the button is clicked
    if small_button.draw(display):
        print("Button clicked!")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()