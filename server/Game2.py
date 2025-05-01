import pygame
import requests
import sys
import os

# כתובת השרת
SERVER_URL = "http://192.168.0.157:5000"

def login_and_get_token(username, password):
    data = {"username": username, "password": password}
    response = requests.post(f"{SERVER_URL}/login", json=data)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        print("Login failed:", response.status_code, response.text)
        return None

def get_player_data(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{SERVER_URL}/get_player", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to get player data:", response.status_code, response.text)
        return None

def show_player_on_screen(player_data):
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Player Viewer")
    clock = pygame.time.Clock()

    player_x = player_data['position_x']
    player_y = player_data['position_y']

    # טוען את התמונה של הדמות
    # הנתיב לקובץ שנמצא תיקייה אחת למעלה בשם graphic
    image_path = os.path.join("..", "graphic", "Standing_front.png")
    try:
        player_image = pygame.image.load(image_path).convert_alpha()
        player_image = pygame.transform.scale(player_image, (50, 80))  # אפשר להתאים לגודל הרצוי
    except pygame.error as e:
        print(f"Failed to load player image: {e}")
        pygame.quit()
        sys.exit()

    running = True
    while running:
        screen.fill((255, 255, 255))  # רקע לבן

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # מציג את הדמות במקום לצייר ריבוע
        screen.blit(player_image, (player_x, player_y))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# קוד ראשי
if __name__ == "__main__":
    username = input("Enter username: ")
    password = input("Enter password: ")

    token = login_and_get_token(username, password)
    if token:
        player_data = get_player_data(token)
        if player_data:
            show_player_on_screen(player_data)
        else:
            print("Failed to retrieve player data.")
    else:
        print("Login failed. Exiting.")

app.run(host='0.0.0.0', port=port, debug=False)
