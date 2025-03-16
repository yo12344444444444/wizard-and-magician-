import pygame
import socket
import pickle
import os

# Server connection settings
HOST = '127.0.0.1'
PORT = 8824
DEFAULT_BUFFER_SIZE = 1024

# Initialize pygame
pygame.init()

# כתובת השרת
SERVER_IP = '127.0.0.1'
SERVER_PORT = 8825
DEFAULT_BUFFER_SIZE = 1024

# יצירת סוקט UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# פונקציה לשליחת בקשה לשרת וקבלת מידע
def get_objects_from_server():
    try:
        request_data = pickle.dumps({"request": "get_objects"})
        client_socket.sendto(request_data, (SERVER_IP, SERVER_PORT))

        response_data, _ = client_socket.recvfrom(DEFAULT_BUFFER_SIZE)
        objects = pickle.loads(response_data)

        print(f"✅ Received objects from server: {objects}")  # הדפסת המידע שהתקבל

        return objects
    except Exception as e:
        print(f"❌ Error communicating with server: {e}")
        return []

def get_objects_from_server():
    try:
        request_data = pickle.dumps({"request": "get_objects"})
        client_socket.sendto(request_data, (SERVER_IP, SERVER_PORT))

        response_data, _ = client_socket.recvfrom(DEFAULT_BUFFER_SIZE)

        print(f"📩 Raw response from server: {response_data}")  # בודקים מה מתקבל

        try:
            objects = pickle.loads(response_data)  # פירוק הנתונים
            print(f"✅ Parsed objects: {objects}")  # מדפיסים לראות מה התקבל
            return objects
        except pickle.UnpicklingError as e:
            print(f"❌ Pickle error: {e}")
            return []

    except Exception as e:
        print(f"❌ Error communicating with server: {e}")
        return []

# מחלקה להצגת אובייקטים
class ObjectPlacer:
    def __init__(self, position, obj_id):
        # בדיקה שהמזהה תקין
        if not isinstance(obj_id, str) or not obj_id.isalnum():
            print(f"⚠️ Invalid ID received: {obj_id}")
            return

        # בניית הנתיב של קובץ התמונה
        image_path = f"graphic/{obj_id}.png"

        # בדיקה האם הקובץ קיים
        if not os.path.exists(image_path):
            print(f"⚠️ Image file not found: {image_path}")
            return

        # טעינת התמונה אם היא קיימת
        self.img = pygame.image.load(image_path)

        # מיקום האובייקט
        self.position = position


# פונקציה ראשית להרצת המשחק
def main():
    screen = pygame.display.set_mode((800, 600))  # יצירת חלון משחק
    pygame.display.set_caption("Wizard and Magician Game")

    objects = get_objects_from_server()  # קבלת מידע מהשרת

    running = True
    while running:
        screen.fill((0, 0, 0))  # רקע שחור

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # יצירת אובייקטים על המסך
        for obj_data in objects:
            print(f"🎮 Processing object: {obj_data}")  # הדפסת הנתונים לפני יצירת האובייקט
            ObjectPlacer((obj_data['x'], obj_data['y']), obj_data['ip'])

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
