import pygame
import requests
import sys
import time
import os
# Initialize Pygame
pygame.init()

# Constants for screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)

# Your API URL

# Pygame screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bot Visualization')

# Font for displaying text
font = pygame.font.SysFont('Arial', 16)
# אחרי ההגדרות שלך:
WORLD_WIDTH  = SCREEN_WIDTH * 40
WORLD_HEIGHT = SCREEN_HEIGHT * 40

auto_walk = False
auto_stage = 0   # 0=למעלה, 1=ימינה, 2=למטה, 3=שמאלה
auto_last_move_time = 0
AUTO_DELAY = 0.05  # השהייה בין צעדים (שניות)

class clientTest():
    def __init__(self, apiUrl, data):
        self.API_URL = apiUrl
        self.data = data

    def handle_auto_movement(self, token, player_data):
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
                    resp = requests.post(f'{self.API_URL}/movement', json=data, headers=headers)
                    if resp.status_code == 200:
                        return resp.json()
                    else:
                        print(f"[AUTO] Movement failed: {resp.status_code}")
                except Exception as e:
                    print(f"[AUTO] Request error: {e}")
                break

        return None

    def draw_health_bar(self,screen, x, y, health, max_health=100):
        bar_width = 40
        bar_height = 6
        health_ratio = health / max_health
        pygame.draw.rect(screen, (255, 0, 0), (x - bar_width//2, y - 30, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (x - bar_width//2, y - 30, int(bar_width * health_ratio), bar_height))


    def load_images(self):
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
    def load_player_image(self):
        try:
            player_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'graphic'))
            print(f"Looking for player image at: {player_path}")
            player_image = pygame.image.load(os.path.join(player_path, 'Standing_front.png')).convert()
            player_image.set_colorkey((0, 0, 0))
            return player_image
        except pygame.error as e:
            print(f"Error loading player image: {e}")
            return None


    # Draw an object relative to the player's position
    def draw_object(self,screen, obj, player_x, player_y, object_images):
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
    def load_object_images(self):
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
    def handle_player_movement(self,token, screen_width, screen_height):
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
                response = requests.post(f'{self.API_URL}/movement', json=data, headers=headers)
                print("movement:", response.json())
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Movement error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Error sending movement: {e}")
        return None

    # Get current player data
    def get_player_data(self, token):
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(f'{self.API_URL}/get_player', headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching player data: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Connection error fetching player data: {e}")
            return None

    # Get full game state
    def get_game_state(self,token, screen_width, screen_height):
        start = time.time()
        try:
            headers = {'Authorization': f'Bearer {token}'}
            data = {'screen_width': screen_width, 'screen_height': screen_height}
            response = requests.post(f'{self.API_URL}/game_state', json=data, headers=headers)
            if response.status_code == 200:
                game_state_data = response.json()
                if 'bots' in game_state_data:
                    print(f"[DEBUG] Received {len(game_state_data['bots'])} bots from server.")
                print(f"get_game_state client: {time.time() - start}")
                return game_state_data
            else:
                print(f"Error fetching game state: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Connection error fetching game state: {e}")
        return None

    # Draw a bot relative to the player
    def draw_bot(self,screen, bot, player_x, player_y, ghost_images):
        print(f"[DEBUG] Drawing bot: {bot}")
        bot_x = bot.get('x', 0)
        bot_y = bot.get('y', 0)
        direction = bot.get('direction', 'front').lower()

        bot_location_x = (bot_x - player_x) + (SCREEN_WIDTH // 2)
        bot_location_y = (bot_y - player_y) + (SCREEN_HEIGHT // 2)

        if direction in ('up', 'back'):
            ghost_img = ghost_images.get('back')
            print(f"[DEBUG] Bot direction: {direction}, using image: back")
        elif direction in ('down', 'front'):
            ghost_img = ghost_images.get('front')
            print(f"[DEBUG] Bot direction: {direction}, using image: front")
        elif direction == 'left':
            ghost_img = ghost_images.get('left')
            print(f"[DEBUG] Bot direction: {direction}, using image: left")
        elif direction == 'right':
            ghost_img = ghost_images.get('right')
            print(f"[DEBUG] Bot direction: {direction}, using image: right")
        else:
            ghost_img = ghost_images.get('front')
            print(f"[DEBUG] Unknown bot direction: {direction}, using image: front")

        if ghost_img:
            img_rect = ghost_img.get_rect(center=(bot_location_x, bot_location_y))
            screen.blit(ghost_img, img_rect)
        else:
            print(f"[WARNING] No image found for bot direction: {direction}")

    def send_attack_request(self,token, x, y, weapon_type, server_url='http://127.0.0.1:5000/attack'):
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
    def draw_player(self,screen, player_image):
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        player_rect = player_image.get_rect(center=(center_x, center_y))
        screen.blit(player_image, player_rect)


    def send_item_drop_to_server(self,items, token):
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
                    response = requests.post(f"{self.API_URL}/drop_item_on_map", json=data, headers=headers)
                    if response.status_code != 200:
                        print(f"Failed to drop item {item['file']} on map: {response.json()}")
                except Exception as e:
                    print(f"Error dropping {item['file']} on map:", e)

    def main(self,token):
        ghost_images = self.load_images()
        player_image = self.load_player_image()
        object_images = self.load_object_images()

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
        player_data = self.get_player_data(token)

        while running:
            start = time.time()
            dropped_items = []
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        global auto_walk
                        auto_walk = not auto_walk
                        print(f"[INFO] Auto walk mode: {'ON' if auto_walk else 'OFF'}")
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    click_world_x = mouse_x + player_data['position_x'] - SCREEN_WIDTH // 2
                    click_world_y = mouse_y + player_data['position_y'] - SCREEN_HEIGHT // 2

                    weapon = "Stone_Sword"  # שים כאן את הנשק הפעיל של השחקן
                    result = self.send_attack_request(token, click_world_x, click_world_y, weapon)
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
                game_state = self.handle_auto_movement(token, player_data)
            else:
                game_state = self.handle_player_movement(token, SCREEN_WIDTH, SCREEN_HEIGHT)
            if not game_state:
                game_state = self.get_game_state(token, SCREEN_WIDTH, SCREEN_HEIGHT)

            # עדכן את player_data מתוך game_state אם יש
            if game_state and 'player' in game_state:
                player_data = game_state['player']
            else:
                player_data = self.get_player_data(token)

            # בדיקה אם השחקן מת
            if player_data and player_data.get('health', 100) <= 0:
                print("[INFO] Player is dead. Attempting to respawn...")
                try:
                    headers = {'Authorization': f'Bearer {token}'}
                    respawn_response = requests.post(f'{self.API_URL}/respawn', headers=headers)
                    if respawn_response.status_code == 200:
                        print("[INFO] Player respawned successfully.")
                        player_data = self.get_player_data(token)
                    else:
                        print(f"[ERROR] Respawn failed: {respawn_response.status_code} - {respawn_response.text}")
                except requests.exceptions.RequestException as e:
                    print(f"[ERROR] Connection error while respawning: {e}")

            # ציור
            screen.fill(GREEN)

            if player_data:
                player_x = player_data.get('position_x', SCREEN_WIDTH // 2)
                player_y = player_data.get('position_y', SCREEN_HEIGHT // 2)
                print(f"[DEBUG] Player position: {player_x}, {player_y}")

                if game_state and 'objects' in game_state:
                    for obj in game_state['objects']:
                        self.draw_object(screen, obj, player_x, player_y, object_images)

                print("dropped_items",dropped_items)
                # שליחת פרטי החפץ לשרת
                self.send_item_drop_to_server(dropped_items, token)

    #            for item in dropped_items:
    #                if item['file'].lower() == 'money':
    #                    continue
    #                try:
    #                    filename = f"{os.path.splitext(item['file'])[0]}_Inventory.png"
    #                    image = pygame.image.load(os.path.join("inventory", filename)).convert_alpha()
    #                    image.set_colorkey((255, 255, 255))
    #                    screen.blit(image, (
    #                        item["x"] - player_x + SCREEN_WIDTH // 2,
    #                        item["y"] - player_y + SCREEN_HEIGHT // 2
    #                    ))
    #                except FileNotFoundError:
    #                    print(f"Image file not found: {filename}")

                if game_state and 'bots' in game_state:
                    for bot in game_state['bots']:
                        self.draw_bot(screen, bot, player_x, player_y, ghost_images)
                self.draw_player(screen, player_image)

            status_text = font.render("Bot Visualization - Press ESC to exit", True, WHITE)
            screen.blit(status_text, (10, 10))
            pygame.display.flip()
    #        clock.tick(FPS)

        pygame.quit()
        sys.exit()
