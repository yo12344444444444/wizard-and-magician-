from flask import Flask, request, jsonify
import sqlite3
from jose import jwt  # Replace PyJWT with jose.jwt
import datetime
from functools import wraps
from flasgger import Swagger
import time
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SWAGGER'] = {
    'title': 'Game API',
    'uiversion': 3,
    'securityDefinitions': {
        'BearerAuth': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Enter token with **Bearer** prefix. Example: "Bearer your_token_here"'
        }
    },
    'security': [{'BearerAuth': []}]
}
swagger = Swagger(app)
app.config['SECRET_KEY'] = 'your_secret_key'
DATABASE = ('../DATABASE_GAME.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing!'}), 403
        try:
            data = jwt.decode(token[7:], app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data['user_id']
        except:
            return jsonify({'error': 'Token is invalid!'}), 403
        return f(user_id=user_id, *args, **kwargs)
    return decorated

@app.route('/')
def home():
    return "Welcome to the Game API!"

@app.route('/login', methods=['POST'])
def login():
    """
    User login
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: myuser
            password:
              type: string
              example: mypass
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Login successful
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            message:
              type: string
              example: Invalid credentials
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE username = ? AND password_hash = ?", (username, password))
    user = cursor.fetchone()

    if user:
     cursor.execute("UPDATE players SET status = 'active' WHERE player_id = ?", (user['player_id'],))
     conn.commit()
     conn.close()

     token = jwt.encode({
         'user_id': user['player_id'],
         'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=10)
     }, app.config['SECRET_KEY'], algorithm='HS256')

     return jsonify({
         'message': 'Login successful',
         'token': token,
         'user': {
             'id': user['player_id'],
             'username': user['username'],
             'position_x': user['position_x'],
             'position_y': user['position_y'],
             'health': user['health'],
             'coins': user['coins'],
             'status': 'active'
         }
     })
    else:
     conn.close()
     return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/logout', methods=['POST'])
@token_required
def logout(user_id):
    """
        Logs out the current user
        ---
        security:
          - BearerAuth: []
        tags:
          - Authentication
        parameters:
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token (e.g., "Bearer <your_token>")
        responses:
          200:
            description: Logout successful
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Logout successful
          401:
            description: Unauthorized - invalid or missing token
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Invalid or expired token
        """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET status = 'inactive' WHERE player_id = ?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User logged out successfully'})

@app.route('/get_player', methods=['GET'])
@token_required
def get_player(user_id):
    """
        Get player details
        ---
        security:
          - BearerAuth: []
        tags:
          - Player
        parameters:
          - name: Authorization
            in: header
            type: string
            required: true
            description: Bearer token (e.g., "Bearer <your_token>")
        responses:
          200:
            description: Player data retrieved successfully
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: Player123
                level:
                  type: integer
                  example: 5
                coins:
                  type: integer
                  example: 120
                location:
                  type: object
                  properties:
                    x:
                      type: integer
                      example: 100
                    y:
                      type: integer
                      example: 200
          401:
            description: Unauthorized - invalid or missing token
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Invalid or expired token
        """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE player_id = ?", (user_id,))
    player = cursor.fetchone()
    conn.close()

    if player:
     return jsonify({
         'player_id': player['player_id'],
         'username': player['username'],
         'position_x': player['position_x'],
         'position_y': player['position_y'],
         'health': player['health'],
         'coins': player['coins'],
         'status': player['status']
     })
    else:
     return jsonify({'error': 'Player not found'}), 404

@app.route('/signup', methods=['POST'])
def signup():
    """
    Register a new user
    ---
    tags:
      - Authentication
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: new_user
            email:
              type: string
              example: user@example.com
            password:
              type: string
              example: secret123
    responses:
      201:
        description: Signup successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: User created successfully
      400:
        description: Bad request or user already exists
        schema:
          type: object
          properties:
            message:
              type: string
              example: Username already exists
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
     cursor.execute("INSERT INTO players (username, password_hash) VALUES (?, ?)", (username, password))
     conn.commit()
     new_id = cursor.lastrowid
     cursor.execute("UPDATE players SET status = 'active' WHERE player_id = ?", (new_id,))
     conn.commit()
    except sqlite3.IntegrityError:
     conn.close()
     return jsonify({'error': 'Username already exists'}), 409

    token = jwt.encode({
     'user_id': new_id,
     'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=10)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    conn.close()
    return jsonify({
     'message': 'User signed up successfully',
     'token': token,
     'player_id': new_id
    })
@app.route('/game_state', methods=['POST'])
@token_required
def game_state(user_id):
    """
    Get updated game state for the player
    ---
    security:
      - BearerAuth: []
    tags:
      - Game
    consumes:
      - application/json
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token (e.g., "Bearer <your_token>")
      - in: body
        name: player_data
        required: true
        schema:
          type: object
          required:
            - direction
            - x
            - y
            - screen_width
            - screen_height
          properties:
            direction:
              type: string
              example: "up"
            x:
              type: integer
              example: 120
            y:
              type: integer
              example: 80
            screen_width:
              type: integer
              example: 1000
            screen_height:
              type: integer
              example: 800
    responses:
      200:
        description: Game state returned successfully
      401:
        description: Unauthorized - token missing or invalid
    """
    data = request.get_json()
    screen_width = data.get('screen_width')
    screen_height = data.get('screen_height')

    # בדוק אם השחקן הותקף ע"י בוטים או שחקנים אחרים
    attack_result = was_player_hit(user_id)

    # קבל את מצב המשחק הכללי
    game_state_data = get_game_state(user_id, screen_width, screen_height)

    # בדוק אם הייתה שגיאה ב־get_game_state
    if "error" in game_state_data:
        return jsonify(game_state_data), 404

    # הוסף מידע על השחקן
    player_status = {
        'was_attacked': attack_result.get('was_attacked', False),
        'new_health': attack_result.get('new_health')
    }

    # אם השחקן מת - נוסיף גם מיקום חדש
    if 'respawn_position' in attack_result:
        player_status['respawn_position'] = attack_result['respawn_position']

    game_state_data['player_status'] = player_status

    return jsonify(game_state_data), 200



def get_game_state(user_id, screen_width, screen_height):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM players WHERE player_id = ?", (user_id,))
    main_player = cursor.fetchone()
    if not main_player:
        conn.close()
        return {'error': 'Player not found'}

    half_width = screen_width / 2
    half_height = screen_height / 2
    center_x = main_player['position_x']
    center_y = main_player['position_y']

    min_x, max_x = center_x - half_width, center_x + half_width
    min_y, max_y = center_y - half_height, center_y + half_height

    cursor.execute("SELECT * FROM players WHERE player_id != ? AND status = 'active'", (user_id,))
    players = [
        {
            'id': f"player{p['player_id']}",
            'name': p['username'],
            'x': p['position_x'],
            'y': p['position_y'],
            'angle': 0,
            'color': '#00ff00',
            'animation_frames': [
                "player_move/Walking_Front.gif",
                "player_move/Walking_Front_2.jpg",
                "player_move/Walking_Left_1.jpg",
                "player_move/Walking_Left_2.jpg",
                "player_move/Walking_Right_1.jpg",
                "player_move/Walking_Right_2.jpg"
            ],
            'idle_frame': "player/Standing_front.jpg"
        }
        for p in cursor.fetchall()
        if min_x <= p['position_x'] <= max_x and min_y <= p['position_y'] <= max_y
    ]

    cursor.execute("SELECT * FROM bots")
    bots = [
        {
            'id': f"bot{b['bot_id']}",
            'x': b['position_x'],
            'y': b['position_y'],
            'type': b['bot_type'],
            'angle': 0,
            'color': '#ff0000',
            'animation_frames': [
                f"bot/{b['bot_type']}_1.png",
                f"bot/{b['bot_type']}_2.png",
                f"bot/{b['bot_type']}_3.png"
            ]
        }
        for b in cursor.fetchall()
        if min_x <= b['position_x'] <= max_x and min_y <= b['position_y'] <= max_y
    ]

    cursor.execute("SELECT * FROM map_objects")
    objects = [
        {
            'id': f"obj{o['object_id']}",
            'x': o['position_x'],
            'y': o['position_y'],
            'size': 40,
            'file': o['file']
        }
        for o in cursor.fetchall()
        if min_x <= o['position_x'] <= max_x and min_y <= o['position_y'] <= max_y
    ]

    conn.close()
    return {
        'players': players,
        'bots': bots,
        'objects': objects
    }

@app.route('/movement', methods=['POST'])
@token_required
def movement(user_id):
    """
    Move Player and return updated game state
    ---
    security:
      - BearerAuth: []
    tags:
      - Game
    consumes:
      - application/json
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token (e.g., "Bearer <your_token>")
      - in: body
        name: player_data
        required: true
        schema:
          type: object
          required:
            - direction
            - x
            - y
            - screen_width
            - screen_height
          properties:
            direction:
              type: string
              example: "d"
            x:
              type: integer
              example: 120
            y:
              type: integer
              example: 80
            screen_width:
              type: integer
              example: 1000
            screen_height:
              type: integer
              example: 800
    responses:
      200:
        description: Game state after movement
      400:
        description: Invalid direction
      404:
        description: Player not found
    """
    data = request.get_json()
    direction = data.get('direction')
    screen_width = data.get('screen_width')
    screen_height = data.get('screen_height')

    # קבלת המהירות מהטבלה של השחקן
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT position_x, position_y, speed FROM players WHERE player_id = ?", (user_id,))
    player = cursor.fetchone()

    if not player:
        conn.close()
        return jsonify({'error': 'Player not found'}), 404

    x, y, speed = player['position_x'], player['position_y'], player['speed']
    move_amount = speed  # המהירות תהיה לפי הערך בטבלה

    if direction not in ['w', 'a', 's', 'd']:
        return jsonify({'error': 'Invalid direction'}), 400

    #  עדכון המיקום של השחקן לפי המהירות וגם בדיקה שלא יצא מגבולות המסך
    if direction == 'w' and y + move_amount <= screen_height * 40:
        y += move_amount
    elif direction == 's' and y - move_amount >= 0:
        y -= move_amount
    elif direction == 'a' and x - move_amount >= 0:
        x -= move_amount
    elif direction == 'd' and x + move_amount <= screen_width * 40:
        x += move_amount

    print(f"player location: x: {x}, y: {y}, speed: {speed}")

    # עדכון מיקום השחקן
    cursor.execute("UPDATE players SET position_x = ?, position_y = ? WHERE player_id = ?", (x, y, user_id))
    conn.commit()
    conn.close()

    # בדיקת אובייקט במיקום החדש
    obj = check_object_at_posiion(x, y)

    # קבלת מצב המשחק (פונקציה צריכה להחזיר dict)
    game_data = get_game_state(user_id, screen_width, screen_height)

    # הוספת אובייקט אם נמצא
    if obj:
        print("found")
        game_data['object_found'] = {
            'name': obj['name'],
            'file': obj['file']
        }

    import json
    print(json.dumps(game_data, indent=2))
    return jsonify(game_data), 200


def is_within_area(center_x, center_y, point_x, point_y, width, height):
    half_w = width // 2
    half_h = height // 2
    return (
        center_x - half_w <= point_x <= center_x + half_w and
        center_y - half_h <= point_y <= center_y + half_h
    )

def check_collision(user_id, x, y):
    conn = get_db_connection()
    cursor = conn.cursor()
    # בדיקת התנגשות עם שחקנים אחרים
    cursor.execute("SELECT player_id, position_x, position_y FROM players WHERE player_id != ?", (user_id,))
    players = cursor.fetchall()
    for player in players:
        if is_within_area(player['position_x'], player['position_y'], x, y, width=80, height=120):
            conn.close()
            return {'collision': True, 'type': 'player', 'user_id': player['player_id']}

    # בדיקת התנגשות עם בוטים
    cursor.execute("SELECT bot_id, position_x, position_y FROM bots")
    bots = cursor.fetchall()
    for bot in bots:
        if is_within_area(bot['position_x'], bot['position_y'], x, y, width=40, height=52):
            conn.close()
            return {'collision': True, 'type': 'bot', 'user_id': bot['bot_id']}

    conn.close()
    return {'collision': False}

@app.route('/attack', methods=['POST'])
@token_required
def attack(user_id):
    """
    attack
    ---
    security:
      - BearerAuth: []
    tags:
      - Game
    consumes:
      - application/json
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token (e.g., "Bearer <your_token>")
      - in: body
        name: player_data
        required: true
        schema:
          type: object
          required:
            - x
            - y
            - weapon_type
          properties:
            x:
              type: integer
              example: 120
            y:
              type: integer
              example: 80
            weapon_type:
              type: string
              example: Stone_Sword
    responses:
      200:
        description: Game state returned successfully
      400:
        description: Invalid weapon type
      401:
        description: Unauthorized - token missing or invalid
      404:
        description: Target not found
    """
    data = request.get_json()
    x = data.get('x')
    y = data.get('y')
    weapon_type = data.get('weapon_type')

    collision_result = check_collision(user_id, x, y)

    if collision_result['collision']:
        target_type = collision_result['type']
        target_user_id = collision_result['user_id']

        weapon_damage = {
            'Stone_Sword': 10,
            'Iron_Sword': 15,
            'Gold_Sword': 20,
            'Wood_Wand': 10,
            'Gold_Wand': 20
        }
        damage = weapon_damage.get(weapon_type, 5)

        conn = get_db_connection()
        cursor = conn.cursor()

        if target_type == 'player':
            cursor.execute("SELECT health FROM players WHERE player_id = ?", (target_user_id,))
            player = cursor.fetchone()
            if not player:
                conn.close()
                return jsonify({'error': 'Player not found'}), 404

            new_health = player['health'] - damage
            # ברירת מחדל respawn למרכז (50,50) — אפשר לשנות
            respawn_x, respawn_y = 50, 50

            if new_health <= 0:
                cursor.execute("""
                        UPDATE players
                          SET health = ?, position_x = ?, position_y = ?, coins = 0
                        WHERE player_id = ?
                    """, (100, respawn_x, respawn_y, target_user_id))
                conn.commit()
                conn.close()

                drops = generate_drops()

                response_data = {
                    'message': 'Bot died and respawned',
                    'target': 'bot',
                    'new_health': 100,
                    'respawn_position': {'x': respawn_x, 'y': respawn_y},
                    'drops': drops
                }
                print(f"Response sent to client: {response_data}")
                return jsonify(response_data), 200

            else:
                cursor.execute(
                    "UPDATE players SET health = ? WHERE player_id = ?",
                    (new_health, target_user_id)
                )
                conn.commit()
                conn.close()

                response_data = {
                    'message': 'Player damaged',
                    'target': 'player',
                    'new_health': new_health
                }
                print(f"Response sent to client: {response_data}")
                return jsonify(response_data), 200

        elif target_type == 'bot':
            cursor.execute("SELECT health FROM bots WHERE bot_id = ?", (target_user_id,))
            bot = cursor.fetchone()
            if not bot:
                conn.close()
                return jsonify({'error': 'Bot not found'}), 404

            new_health = bot['health'] - damage
            respawn_x, respawn_y = 50, 50  # נקודת respawn לבוט

            if new_health <= 0:
                cursor.execute("""
                        UPDATE bots
                          SET health = ?, position_x = ?, position_y = ?
                        WHERE bot_id = ?
                    """, (100, respawn_x, respawn_y, target_user_id))
                conn.commit()
                conn.close()
                drops = generate_drops()

                response_data = {
                    'message': 'Player died and respawned',
                    'target': 'player',
                    'new_health': 100,
                    'respawn_position': {'x': respawn_x, 'y': respawn_y},
                    'drops': drops
                }
                print(f"Response sent to client: {response_data}")
                return jsonify(response_data), 200

            else:
                cursor.execute(
                    "UPDATE bots SET health = ? WHERE bot_id = ?",
                    (new_health, target_user_id)
                )
                conn.commit()
                conn.close()

                response_data = {
                    'message': 'Bot damaged',
                    'target': 'bot',
                    'new_health': new_health
                }
                print(f"Response sent to client: {response_data}")
                return jsonify(response_data), 200

def generate_drops():
    possible_drops = ["money", "apple", "bush", "Dark_Potion", "Life_Potion", "Fire_Potion", "Poison_Potion"]
    return random.sample(possible_drops, 2)
    # אם לא פגיעה

def was_player_hit(player_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # קבלת מיקום וחיים של השחקן
    cursor.execute("SELECT position_x, position_y, health FROM players WHERE player_id = ?", (player_id,))
    player = cursor.fetchone()

    if not player:
        conn.close()
        return {'was_attacked': False}

    player_x = player['position_x']
    player_y = player['position_y']
    player_health = player['health']

    # קבלת בוטים
    cursor.execute("SELECT bot_id, position_x, position_y, last_attack_time FROM bots")
    bots = cursor.fetchall()

    current_time = int(time.time())
    was_attacked = False
    player_died = False
    respawn_position = None

    # טיפול בפגיעות מבוטים
    for bot in bots:
        bot_id = bot['bot_id']
        bot_x = bot['position_x']
        bot_y = bot['position_y']
        last_attack = bot['last_attack_time']

        if abs(bot_x - player_x) < 100 and abs(bot_y - player_y) < 100:
            if current_time - last_attack >= 5:
                new_health = max(player_health - 10, 0)
                was_attacked = True

                if new_health <= 0:
                    respawn_x, respawn_y = 50, 50
                    cursor.execute("""
                        UPDATE players
                        SET health = ?, position_x = ?, position_y = ?, coins = 0
                        WHERE player_id = ?
                    """, (100, respawn_x, respawn_y, player_id))
                    player_died = True
                    respawn_position = {'x': respawn_x, 'y': respawn_y}
                    player_health = 100
                else:
                    cursor.execute("UPDATE players SET health = ? WHERE player_id = ?", (new_health, player_id))
                    player_health = new_health

                cursor.execute("UPDATE bots SET last_attack_time = ? WHERE bot_id = ?", (current_time, bot_id))

    # טיפול בפגיעות משחקנים אחרים
    cursor.execute("SELECT player_id, position_x, position_y, last_attack_time FROM players WHERE player_id != ?", (player_id,))
    other_players = cursor.fetchall()

    for p in other_players:
        other_id = p['player_id']
        other_x = p['position_x']
        other_y = p['position_y']
        last_attack = p['last_attack_time']

        if abs(other_x - player_x) < 100 and abs(other_y - player_y) < 100:
            if current_time - last_attack >= 5:
                new_health = max(player_health - 10, 0)
                was_attacked = True

                if new_health <= 0:
                    respawn_x, respawn_y = 50, 50
                    cursor.execute("""
                        UPDATE players
                        SET health = ?, position_x = ?, position_y = ?, coins = 0
                        WHERE player_id = ?
                    """, (100, respawn_x, respawn_y, player_id))
                    player_died = True
                    respawn_position = {'x': respawn_x, 'y': respawn_y}
                    player_health = 100
                else:
                    cursor.execute("UPDATE players SET health = ? WHERE player_id = ?", (new_health, player_id))
                    player_health = new_health

                cursor.execute("UPDATE players SET last_attack_time = ? WHERE player_id = ?", (current_time, other_id))

    conn.commit()
    conn.close()

    response = {
        'was_attacked': was_attacked,
        'new_health': player_health
    }

    if player_died:
        response['respawn_position'] = respawn_position

    print(response)
    return response


def check_object_at_posiion(x: int, y: int):
    """
    בודקת אם יש אובייקט במיקום המסוים ומחזירה את שמו והקובץ שלו אם קיים.

    :param x: קואורדינטת X
    :param y: קואורדינטת Y
    :return: dict עם מידע על האובייקט אם נמצא, אחרת None
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, file FROM map_objects WHERE position_x = ? AND position_y = ?
    """, (x, y))
    obj = cursor.fetchone()
    conn.close()

    if obj:
        return {
            'found': True,
            'name': obj['name'],
            'file': obj['file']
        }
    else:
        return None


@app.route('/add-to-inventory', methods=['POST'])
@token_required
def add_to_inventory(user_id):
    """
    Add Object to Inventory
    ---
    security:
      - BearerAuth: []
    tags:
      - Game
    consumes:
      - application/json
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token (e.g., "Bearer <your_token>")
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - object_name
            - slot_index
            - has_space_in_inventory
          properties:
            object_name:
              type: string
              example: "potion_red"
              description: The name of the object to add to inventory
            slot_index:
              type: integer
              example: 3
              description: The index of the inventory slot
            has_space_in_inventory:
              type: boolean
              example: true
              description: Whether the inventory has space for this item
    responses:
      200:
        description: The object was successfully added to the inventory or relevant status was returned
      400:
        description: Missing or invalid data in request
      401:
        description: Unauthorized - token missing or invalid
      404:
        description: Object not found on the map
    """
    data = request.get_json()
    object_name = data.get('object_name')
    has_space = data.get('has_space_in_inventory')
    player_id = user_id
    slot_index = data.get('slot_index')

    if None in (object_name, has_space, player_id, slot_index):
        return jsonify({'error': 'Missing data'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # שליפת האובייקט לפי הקוד
    cursor.execute("""
        SELECT * FROM map_objects WHERE name = ?
    """, (object_name,))
    obj = cursor.fetchone()

    if not obj:
        conn.close()
        return jsonify({'success': False, 'message': 'Object not found'}), 404

    if not has_space:
        conn.close()
        return jsonify({'success': False, 'message': 'No space in inventory'}), 200

    if obj['name'] in ['tree', 'bush']:
        conn.close()
        return jsonify({'success': False, 'message': 'Object cannot be added to inventory'}), 200

    # בדיקה אם האובייקט כבר קיים בתא הזה של השחקן
    cursor.execute("""
        SELECT * FROM inventory
        WHERE player_id = ? AND name = ? AND slot_index = ?
    """, (player_id, obj['name'], slot_index))
    existing_item = cursor.fetchone()

    if existing_item:
        # הגדלת כמות ב-1
        cursor.execute("""
            UPDATE inventory
            SET quantity = quantity + 1
            WHERE inventory_id = ?
        """, (existing_item['inventory_id'],))
    else:
        # יצירת פריט חדש עם כמות 1
        cursor.execute("""
            INSERT INTO inventory (player_id, name, slot_index, quantity)
            VALUES (?, ?, ?, 1)
        """, (player_id, obj['name'], slot_index))

    # הסרה מהמפה
    cursor.execute("""
        DELETE FROM map_objects WHERE object_id = ?
    """, (obj['object_id'],))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f'{object_name} added to inventory'}), 200

@app.route('/use_object', methods=['POST'])
@token_required
def use_object(user_id):
    """
    Use an object like apple, blueberry, or a potion
    ---
    security:
      - BearerAuth: []
    tags:
      - Game
    consumes:
      - application/json
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token (e.g., "Bearer <your_token>")
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            object_type:
              type: string
              example: "Poison_Potion"
    responses:
      200:
        description: Effect applied
    """
    data = request.get_json()
    obj_type = data.get('object_type')
    conn = get_db_connection()
    cursor = conn.cursor()
    effect = None

    if obj_type == 'apple':
        cursor.execute("UPDATE players SET health = health + 10 WHERE player_id = ?", (user_id,))
        effect = 'Added 10 health'

    elif obj_type == 'blueberry':
        cursor.execute("UPDATE players SET health = health + 5 WHERE player_id = ?", (user_id,))
        effect = 'Added 5 health'

    elif obj_type == 'Dark_Potion':
        # שלב 1: קבל את מיקום השחקן
        cursor.execute("SELECT position_x, position_y FROM players WHERE player_id = ?", (user_id,))

        player = cursor.fetchone()
        px, py = player['position_x'], player['position_y']

        # שלב 2: הורדת חיים משחקנים אחרים בטווח
        cursor.execute("SELECT player_id, position_x, position_y FROM players WHERE player_id != ?", (user_id,))
        others = cursor.fetchall()
        for other in others:
            ox, oy = other['position_x'], other['position_y']
            dx = px - ox
            dy = py - oy
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance <= 30:
                cursor.execute("UPDATE players SET health = health - 50 WHERE player_id = ?", (other['player_id'],))

        # שלב 3: הורדת חיים גם לבוטים בטווח (אם יש טבלת בוטים)
        cursor.execute("SELECT bot_id, position_x, position_y FROM bots")
        bots = cursor.fetchall()
        for bot in bots:
            bx, by = bot['position_x'], bot['position_y']
            dx = px - bx
            dy = py - by
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance <= 30:
                cursor.execute("UPDATE bots SET health = health - 50 WHERE bot_id = ?", (bot['bot_id'],))
        effect = 'Dark potion activated: -50 HP to enemies and bots within 30px range'

    elif obj_type == 'Life_Potion':
        # Placeholder: either +70 instantly or +10 for 7 seconds
        cursor.execute("UPDATE players SET health = health + 70 WHERE player_id = ?", (user_id,))
        effect = 'Life potion used: +70 health'

    elif obj_type == 'Fire_Potion':
        cursor.execute("UPDATE players SET speed = 8 WHERE player_id = ?", (user_id,))
        effect = 'Fire potion used: speed increased to 8 for 20s'

    conn.commit()
    conn.close()
    return jsonify({'effect': effect}), 200

@app.route('/buy_object', methods=['POST'])
@token_required
def buy_object(user_id):
    """
    Buy an object and add it to the player's inventory
    ---
    security:
      - BearerAuth: []
    tags:
      - Game
    consumes:
      - application/json
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token (e.g., "Bearer <your_token>")
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - object_name
            - amount
            - slot_index
          properties:
            object_name:
              type: string
              example: "apple"
            amount:
              type: integer
              example: 20
            slot_index:
              type: integer
              example: 2
    responses:
      200:
        description: Object added to inventory
      400:
        description: Not enough money
      404:
        description: Player not found
    """
    data = request.get_json()
    object_name = data.get('object_name')
    amount = data.get('amount')
    slot_index = data.get('slot_index')

    if object_name is None or amount is None or slot_index is None:
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check current player money
    cursor.execute("SELECT coins FROM players WHERE player_id = ?", (user_id,))
    player = cursor.fetchone()

    if not player:
        conn.close()
        return jsonify({'error': 'Player not found'}), 404

    current_money = player['coins']

    if current_money < amount:
        conn.close()
        return jsonify({'error': 'Not enough money'}), 400

    # Subtract money
    cursor.execute("UPDATE players SET coins = coins - ? WHERE player_id = ?", (amount, user_id))

    # Add object to inventory
    cursor.execute(
        """
        INSERT INTO inventory (player_id, name, slot_index, quantity)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(player_id, name)
        DO UPDATE SET quantity = quantity + 1
        """,
        (user_id, object_name, slot_index)
    )

    conn.commit()
    conn.close()

    return jsonify({'message': f'{object_name} added to inventory. {amount} money deducted.'}), 200


if __name__ == '__main__':
    app.run(debug=True)
