import pygame
import requests
import threading
import json
import time
import os
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
FPS = 60

# מיקום שחקן אמיתי בעולם (קואורדינטות עולמיות)
player_x = 5
player_y = 5
player_direction = "down"

# משתנים למצלמה
camera_x = 0
camera_y = 0

# מידע חיבור - למלא רק אם יש לך שרת אמיתי פעיל
SERVER_URL = None  # השאר None כדי להשתמש רק בבוטים מקומיים
TOKEN = None  # למלא אם SERVER_URL לא None

# הכנת משתנים גלובליים
bot_images = {}
player_images = {}
bots_data = []
lock = threading.Lock()
debug_log_file = "debug_log.txt"


# פונקציה לכתיבת מידע דיבוג לקובץ
def log_debug(message):
    with open(debug_log_file, "a", encoding="utf-8") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")
    print(message)


# יצירת קובץ לוג חדש
def create_new_log():
    with open(debug_log_file, "w", encoding="utf-8") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] Debug log started\n")


# פונקציה: עדכון תנועת הבוטים
def update_bots_movement():
    global bots_data

    with lock:
        for bot in bots_data:
            # וודא שהבוט כולל את כל המידע הדרוש
            if "x" not in bot or "y" not in bot:
                continue

            # אם אין מהירות תנועה לבוט, הוסף אותה
            if "move_speed" not in bot:
                bot["move_speed"] = random.uniform(0.2, 0.7)

            # אם אין כיוון תנועה או צריך לשנות כיוון
            if "move_direction" not in bot or random.random() < 0.02:
                directions = ["up", "down", "left", "right"]
                bot["move_direction"] = random.choice(directions)
                bot["direction"] = bot["move_direction"]

            # עדכון מיקום הבוט לפי הכיוון והמהירות
            direction = bot["move_direction"]
            speed = bot["move_speed"]

            # חישוב המיקום החדש
            if direction == "up":
                bot["y"] -= speed
            elif direction == "down":
                bot["y"] += speed
            elif direction == "left":
                bot["x"] -= speed
            elif direction == "right":
                bot["x"] += speed

            # בוטים יכולים לנוע בכל העולם ללא הגבלה - הסרנו את הגבולות כדי שנוכל לראות בוטים רחוקים גם מחוץ לגבולות המסך המקורי


# הוספת בוטים סטטיים למשחק
def add_static_test_bots():
    global bots_data
    with lock:
        # נוסיף כמה בוטים סטטיים לבדיקת התצוגה
        test_bots = [
            {"id": "test1", "x": 3, "y": 3, "direction": "down"},
            {"id": "test2", "x": 6, "y": 4, "direction": "up"},
            {"id": "test3", "x": 9, "y": 6, "direction": "left"},
            {"id": "test4", "x": 12, "y": 8, "direction": "right"},
            # הוספת עוד בוטים רנדומליים למסך - נפזר אותם בטווח רחב יותר כדי לראות שהמצלמה עובדת
            {"id": "bot5", "x": random.randint(-10, 30), "y": random.randint(-10, 30), "direction": "down"},
            {"id": "bot6", "x": random.randint(-10, 30), "y": random.randint(-10, 30), "direction": "up"},
            {"id": "bot7", "x": random.randint(-10, 30), "y": random.randint(-10, 30), "direction": "left"},
            {"id": "bot8", "x": random.randint(-10, 30), "y": random.randint(-10, 30), "direction": "right"}
        ]
        bots_data.extend(test_bots)
        log_debug(f"Added {len(test_bots)} static test bots")


# פונקציה לקבלת נתוני המשחק מהשרת
def get_game_state_thread():
    global bots_data

    # אם אין כתובת שרת, חזור ואל תעשה כלום
    if SERVER_URL is None:
        return

    try:
        url = SERVER_URL
        headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

        data = {
            "x": player_x * TILE_SIZE,
            "y": player_y * TILE_SIZE,
            "direction": player_direction,
            "screen_width": SCREEN_WIDTH,
            "screen_height": SCREEN_HEIGHT
        }

        log_debug(f"Requesting data from server...")
        response = requests.post(url, json=data, headers=headers, timeout=5)

        if response.status_code == 200:
            try:
                game_state = response.json()

                # בדיקה אם יש מפתח 'bots' בתשובה
                if "bots" in game_state:
                    all_bots = game_state["bots"]
                    log_debug(f"Received {len(all_bots)} bots from server")

                    # יצירת מילון של בוטים ייחודיים לפי מזהה
                    unique_bots = {}
                    for bot in all_bots:
                        key = bot.get("id", f"{bot.get('x')}_{bot.get('y')}")
                        unique_bots[key] = bot

                    with lock:
                        # שמירת המידע החדש על בוטים, אבל שמירה על מידע התנועה מהמצב הקודם
                        existing_bots = {bot.get("id", f"{bot.get('x')}_{bot.get('y')}"): bot for bot in bots_data}

                        for key, bot in unique_bots.items():
                            if key in existing_bots:
                                # העתקת מידע התנועה אם קיים
                                if "move_direction" in existing_bots[key]:
                                    bot["move_direction"] = existing_bots[key]["move_direction"]
                                if "move_speed" in existing_bots[key]:
                                    bot["move_speed"] = existing_bots[key]["move_speed"]

                        bots_data = list(unique_bots.values())
                        log_debug(f"Updated bots_data with {len(bots_data)} unique bots")
                else:
                    log_debug(f"No 'bots' key in server response. Response keys: {list(game_state.keys())}")
            except Exception as e:
                log_debug(f"Failed to parse server response: {str(e)}")
        else:
            log_debug(f"Server error: {response.status_code} - {response.text[:100]}...")

    except Exception as e:
        log_debug(f"Error connecting to server: {str(e)}")

    # הפעל שוב את הפונקציה לאחר 2 שניות
    threading.Timer(2.0, get_game_state_thread).start()


def load_images():
    try:
        # ניסיון לטעון תמונות מהנתיב המקורי
        image_paths = {
            "up": "graphic/Ghost_Back.png",
            "down": "graphic/Ghost_Front.png",
            "left": "graphic/Ghost_Left.png",
            "right": "graphic/Ghost_Right.png"
        }

        bot_imgs = {}
        for direction, path in image_paths.items():
            if os.path.exists(path):
                bot_imgs[direction] = pygame.image.load(path)
                log_debug(f"Loaded image: {path}")
            else:
                log_debug(f"Image not found: {path}")
                # יצירת תמונת גיבוי צבעונית
                img = pygame.Surface((TILE_SIZE, TILE_SIZE))

                # צבעים שונים לכיוונים שונים
                if direction == "up":
                    color = (0, 0, 255)  # כחול
                elif direction == "down":
                    color = (255, 0, 0)  # אדום
                elif direction == "left":
                    color = (0, 255, 0)  # ירוק
                elif direction == "right":
                    color = (255, 255, 0)  # צהוב

                img.fill(color)
                bot_imgs[direction] = img
                log_debug(f"Created backup image for: {direction}")

        # אותן תמונות לשחקן (אפשר לשנות בהמשך)
        player_imgs = bot_imgs.copy()

        return bot_imgs, player_imgs

    except Exception as e:
        log_debug(f"Error loading images: {str(e)}")
        # תמונות פשוטות לגיבוי במקרה של בעיה
        empty_surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        empty_surface.fill((255, 0, 0))  # צבע אדום לסימון שגיאה

        backup_imgs = {"up": empty_surface, "down": empty_surface, "left": empty_surface, "right": empty_surface}
        return backup_imgs, backup_imgs


# פונקציה מעודכנת לציור רשת הרקע - עכשיו מתחשבת בהיסט המצלמה
def draw_grid(screen, camera_x, camera_y):
    # חישוב נקודת ההתחלה של הרשת בהתאם למיקום המצלמה
    start_x = (-camera_x * TILE_SIZE) % TILE_SIZE
    start_y = (-camera_y * TILE_SIZE) % TILE_SIZE

    # ציור הקווים האנכיים
    for x in range(int(start_x), SCREEN_WIDTH, TILE_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, SCREEN_HEIGHT))

    # ציור הקווים האופקיים
    for y in range(int(start_y), SCREEN_HEIGHT, TILE_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (SCREEN_WIDTH, y))

    # הוספת סימון לנקודת האפס העולמית (0,0) - אם היא נראית במסך
    world_zero_x = int((0 - camera_x) * TILE_SIZE)
    world_zero_y = int((0 - camera_y) * TILE_SIZE)

    if 0 <= world_zero_x < SCREEN_WIDTH and 0 <= world_zero_y < SCREEN_HEIGHT:
        pygame.draw.circle(screen, (255, 0, 255), (world_zero_x, world_zero_y), 5)


# פונקציה מעודכנת לציור הבוטים - עם התחשבות בהיסט המצלמה
def draw_bots(screen, bots, images, camera_x, camera_y):
    for i, bot in enumerate(bots):
        try:
            # בדיקת תקינות המידע
            if "x" not in bot or "y" not in bot:
                continue

            # חישוב מיקום במסך בהתחשב בהיסט המצלמה
            screen_x = int((bot["x"] - camera_x) * TILE_SIZE)
            screen_y = int((bot["y"] - camera_y) * TILE_SIZE)

            # בדיקה אם הבוט בכלל נראה במסך (אופטימיזציה)
            if screen_x < -TILE_SIZE or screen_x > SCREEN_WIDTH or screen_y < -TILE_SIZE or screen_y > SCREEN_HEIGHT:
                continue

            direction = bot.get("direction", "down")
            if direction not in images:
                direction = "down"  # ברירת מחדל

            image = images[direction]
            screen.blit(image, (screen_x, screen_y))

            # הצגת מידע על הבוט
            font = pygame.font.SysFont(None, 16)
            bot_id = str(bot.get("id", f"{i + 1}"))[:6]
            text = font.render(f"{bot_id}", True, (255, 255, 0))
            screen.blit(text, (screen_x, screen_y - 15))

        except Exception as e:
            log_debug(f"Error drawing bot {i}: {str(e)}")


# פונקציה מעודכנת לציור השחקן - תמיד יהיה במרכז המסך
def draw_player(screen, player_direction, images):
    try:
        # מיקום השחקן במרכז המסך
        center_x = SCREEN_WIDTH // 2 - TILE_SIZE // 2
        center_y = SCREEN_HEIGHT // 2 - TILE_SIZE // 2

        image = images.get(player_direction, images["down"])
        screen.blit(image, (center_x, center_y))

        # הצגת מידע על השחקן
        font = pygame.font.SysFont(None, 16)
        text = font.render("Player", True, (0, 255, 0))
        screen.blit(text, (center_x, center_y - 15))

    except Exception as e:
        log_debug(f"Error drawing player: {str(e)}")


def main():
    global player_x, player_y, player_direction, camera_x, camera_y

    # איפוס קובץ הלוג
    create_new_log()
    log_debug("Game starting...")

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Game State Debugger - Camera Following Player")
    clock = pygame.time.Clock()

    # אתחול גופנים
    pygame.font.init()

    # טעינת תמונות
    global bot_images, player_images
    bot_images, player_images = load_images()

    # הוספת בוטים סטטיים לבדיקה
    add_static_test_bots()

    # התחלת צריכת הנתונים מהשרת אם מוגדר
    if SERVER_URL is not None:
        get_game_state_thread()
        log_debug(f"Server connection enabled. Using URL: {SERVER_URL}")
    else:
        log_debug("Server connection disabled. Using only static bots.")

    log_debug("Main game loop starting...")
    running = True
    show_debug = True
    last_toggle_time = 0
    last_movement_update = time.time()
    move_cooldown = 0.1  # זמן המתנה בשניות בין תנועות
    last_move_time = 0

    while running:
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # לחיצה על D תחליף מצב דיבוג
                if event.key == pygame.K_d and current_time - last_toggle_time > 0.5:
                    show_debug = not show_debug
                    last_toggle_time = current_time
                    log_debug(f"Debug display {'enabled' if show_debug else 'disabled'}")

        # בדיקת תנועה עם קולדאון למניעת תנועה מהירה מדי
        if current_time - last_move_time > move_cooldown:
            keys = pygame.key.get_pressed()
            moved = False

            if keys[pygame.K_UP]:
                player_y -= 1
                player_direction = "up"
                moved = True
            elif keys[pygame.K_DOWN]:
                player_y += 1
                player_direction = "down"
                moved = True
            elif keys[pygame.K_LEFT]:
                player_x -= 1
                player_direction = "left"
                moved = True
            elif keys[pygame.K_RIGHT]:
                player_x += 1
                player_direction = "right"
                moved = True

            if moved:
                last_move_time = current_time
                log_debug(f"Player moved to ({player_x}, {player_y}) facing {player_direction}")

        # עדכון המצלמה להתמקד בשחקן
        camera_x = player_x - (SCREEN_WIDTH / TILE_SIZE / 2) + 0.5  # הוספנו 0.5 כדי שהשחקן יהיה בדיוק במרכז
        camera_y = player_y - (SCREEN_HEIGHT / TILE_SIZE / 2) + 0.5  # הוספנו 0.5 כדי שהשחקן יהיה בדיוק במרכז

        # עדכון תנועת הבוטים (כל 50 מילישניות)
        if current_time - last_movement_update > 0.05:
            update_bots_movement()
            last_movement_update = current_time

        # עדכון וציור המסך
        screen.fill((30, 30, 30))
        draw_grid(screen, camera_x, camera_y)

        # ציור בוטים ושחקן
        with lock:
            bot_count = len(bots_data)
            draw_bots(screen, bots_data, bot_images, camera_x, camera_y)

        # ציור השחקן במרכז המסך
        draw_player(screen, player_direction, player_images)

        # ציור מידע דיבוג
        if show_debug:
            font = pygame.font.SysFont(None, 24)
            info_lines = [
                f"FPS: {int(clock.get_fps())}",
                f"Bots: {bot_count}",
                f"Player: ({player_x}, {player_y})",
                f"Camera: ({camera_x:.1f}, {camera_y:.1f})",
                "Press D to toggle debug info",
                "Server: " + ("Connected" if SERVER_URL else "Disabled")
            ]

            for i, line in enumerate(info_lines):
                text = font.render(line, True, (255, 255, 255))
                screen.blit(text, (10, 10 + i * 25))

        pygame.display.flip()
        clock.tick(FPS)

    log_debug("Game ended")
    pygame.quit()


if __name__ == "__main__":
    main()