import json
import socket

from flask import Flask, request, jsonify
from jose import jwt  # Replace PyJWT with jose.jwt
import os
from functools import wraps
from flasgger import Swagger
import threading

import findy
from functionsServer import *

def move_bots():
    bots = get_all_bots()
    players = get_all_players()
    # בניית cache בזיכרון לעדכונים מהירים
    bot_cache = {
        bot['bot_id']: {
            'bot': bot,
            'last_direction': bot['last_direction'],
            'x': bot['position_x'],
            'y': bot['position_y']
        }
        for bot in bots
    }

    while True:
        tuples = []
        for bot_id, data in bot_cache.items():
            if bot_id>5:
                continue
            bot = data['bot']
            last_direction = data['last_direction']
            x = data['x']
            y = data['y']

            closest_player_id, player_x, player_y = get_closest_player(x, y, players)
            if closest_player_id is None:
                continue
            print("player x: ",player_x, "palyer_y: ",player_y)
            dx, dy = calculate_dx_dy(x, y, player_x, player_y)
            print("the dx is: ",dx,"the dy is: ",dy)
            chosen = choose_direction(last_direction, dx, dy)
            result = bot_action(chosen, bot)
            if result:
                # אם הבוט זז – מעדכנים הכל כולל ההדפסה
                if len(result) == 4:
                    new_x, new_y, bot_id, new_direction = result
                    data['x'] = new_x
                    data['y'] = new_y
                    data['last_direction'] = new_direction
                    # עדכון גם באובייקט הבוט עצמו
                    data['bot']['position_x'] = new_x
                    data['bot']['position_y'] = new_y
                    data['bot']['last_direction'] = new_direction
                    tuples.append(result)
                elif len(result) == 2:
                    bot_id, new_direction = result
                    data['last_direction'] = new_direction
                    data['bot']['last_direction'] = new_direction

                # הדפסה אחרי עדכון — כאן נראה את הערכים החדשים
                print(data['bot'])

        save_tuples(tuples)
        print("____________________________________________________")
        time.sleep(1.5)

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
@app.route('/end', methods=['POST'])
def index():
    data = request.get_json()
    lb.send_player_data(data["username"])
    return jsonify({'message': 'Game API is running'})
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
    conn.row_factory = sqlite3.Row  # To access rows as dictionaries
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE username = ? AND password_hash = ?", (username, password))
    user = cursor.fetchone()

    if user:
        player_id = user['player_id']
        cursor.execute("UPDATE players SET status = 'active' WHERE player_id = ?", (player_id,))

        # Check if inventory already exists
        cursor.execute("SELECT COUNT(*) as count FROM inventory WHERE player_id = ?", (player_id,))
        inventory_count = cursor.fetchone()['count']

        # If no items in inventory, add starter items
        if inventory_count == 0:
            starter_items = [
                ('Wood_Wand', 1),
                ('Stone_Sword', 2)
            ]
            for name, slot_index in starter_items:
                cursor.execute("""
                    INSERT INTO inventory (player_id, name, slot_index, quantity)
                    VALUES (?, ?, ?, ?)
                """, (player_id, name, slot_index, 1))

        conn.commit()
        conn.close()

        token = jwt.encode({
            'user_id': player_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=10)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': player_id,
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
    User signup
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
              example: newuser
            password:
              type: string
              example: newpass
    responses:
      200:
        description: Signup successful
      400:
        description: User already exists
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("SELECT * FROM players WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'User already exists'}), 400

    # Create new user
    cursor.execute("""
        INSERT INTO players (username, password_hash, position_x, position_y, health, coins, status, speed, last_attack)
        VALUES (?, ?, 0, 100, 100, 100, 'active', 3 ,1)
    """, (username, password))
    player_id = cursor.lastrowid

    # Add starter items to inventory
    starter_items = [
        ('Wood_Wand', 1),
        ('Stone_Sword', 2)
    ]
    for name, slot_index in starter_items:
        cursor.execute("""
            INSERT INTO inventory (player_id, name, slot_index, quantity)
            VALUES (?, ?, ?, ?)
        """, (player_id, name, slot_index, 1))

    # Get full user data
    cursor.execute("SELECT * FROM players WHERE player_id = ?", (player_id,))
    user = cursor.fetchone()

    # Generate token
    token = jwt.encode({
        'user_id': player_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=10)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    conn.commit()
    conn.close()

    return jsonify({
        'message': 'Signup successful',
        'token': token,
        'user': {
            'id': player_id,
            'username': user['username'],
            'position_x': user['position_x'],
            'position_y': user['position_y'],
            'health': user['health'],
            'coins': user['coins'],
            'status': user['status']
        }
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
    start = time.time()
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
                "player_move/Walking_Front_2.png",
                "player_move/Walking_Left_1.png",
                "player_move/Walking_Left_2.png",
                "player_move/Walking_Right_1.png",
                "player_move/Walking_Right_2.png"
            ],
            'idle_frame': "player/Standing_front.png"
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
    objects = []
    for o in cursor.fetchall():
        if min_x <= o['position_x'] <= max_x and min_y <= o['position_y'] <= max_y:
            file_name = o['file']
            base_name, ext = os.path.splitext(file_name)
            objects.append({
                'name': f"{o['name']}",
                'x': o['position_x'],
                'y': o['position_y'],
                'size': 40,
                'file': f"{base_name}.png"  # Force the .png extension
            })

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

    screens_x = 8
    screens_y = 5
    if direction == 'w' and y - move_amount >= 0:
        y -= move_amount
    elif direction == 's' and y + move_amount <= screen_height * screens_y:
        y += move_amount
    elif direction == 'a' and x - move_amount >= 0:
        x -= move_amount
    elif direction == 'd' and x + move_amount <= screen_width * screens_x:
        x += move_amount

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
        game_data['object_found'] = {
            'name': obj['name'],
            'file': obj['file']
        }

    import json
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

import math

def is_in_attack_range(attacker_pos, target_pos, range_px):
    dx = attacker_pos['x'] - target_pos['x']
    dy = attacker_pos['y'] - target_pos['y']
    distance = math.sqrt(dx**2 + dy**2)
    return distance <= range_px

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
      200:`
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
    if not collision_result['collision']:
        return jsonify({'message': 'No collision detected'}), 200

    target_type = collision_result['type']
    target_user_id = collision_result['user_id']

    weapon_damage = {
        'Stone_Sword': 10,
        'Iron_Sword': 15,
        'Gold_Sword': 20,
        'Wood_Wand': 10,
        'Gold_Wand': 20
    }

    weapon_range_map = {
        'Stone_Sword': 150,
        'Iron_Sword': 150,
        'Gold_Sword': 150,
        'Wood_Wand': 250,
        'Gold_Wand': 150
    }

    damage = weapon_damage.get(weapon_type, 5)
    weapon_range = weapon_range_map.get(weapon_type, 150)

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT position_x, position_y FROM players WHERE player_id = ?", (user_id,))
    attacker = cursor.fetchone()
    if not attacker:
        conn.close()
        return jsonify({'error': 'Attacker not found'}), 404

    attacker_pos = {'x': attacker['position_x'], 'y': attacker['position_y']}

    # עדכון זמן התקיפה האחרון של התוקף
    cursor.execute("UPDATE players SET last_attack_time = ? WHERE player_id = ?",
                   (datetime.datetime.utcnow(), user_id))

    if target_type == 'player':
        cursor.execute("SELECT position_x, position_y, health FROM players WHERE player_id = ?", (target_user_id,))
        target = cursor.fetchone()
        if not target:
            conn.close()
            return jsonify({'error': 'Player not found'}), 404

        target_pos = {'x': target['position_x'], 'y': target['position_y']}
        if not is_in_attack_range(attacker_pos, target_pos, weapon_range):
            conn.close()
            return jsonify({'message': 'Target out of range'}), 200

        new_health = target['health'] - damage
        if new_health <= 0:
            respawn_x, respawn_y = 50, 50
            cursor.execute("""
                UPDATE players
                SET health = 100, position_x = ?, position_y = ?, coins = 0
                WHERE player_id = ?
            """, (respawn_x, respawn_y, target_user_id))
            drops = generate_drops()
            conn.commit()
            conn.close()
            return jsonify({
                'message': 'Player died and respawned',
                'target': 'player',
                'new_health': 100,
                'respawn_position': {'x': respawn_x, 'y': respawn_y},
                'drops': drops
            }), 200
        else:
            cursor.execute("UPDATE players SET health = ? WHERE player_id = ?", (new_health, target_user_id))
            conn.commit()
            conn.close()
            return jsonify({
                'message': 'Player damaged',
                'target': 'player',
                'new_health': new_health
            }), 200

    elif target_type == 'bot':
        cursor.execute("SELECT position_x, position_y, health FROM bots WHERE bot_id = ?", (target_user_id,))
        bot = cursor.fetchone()
        if not bot:
            conn.close()
            return jsonify({'error': 'Bot not found'}), 404

        target_pos = {'x': bot['position_x'], 'y': bot['position_y']}
        if not is_in_attack_range(attacker_pos, target_pos, weapon_range):
            conn.close()
            return jsonify({'message': 'Target out of range'}), 200

        new_health = bot['health'] - damage
        if new_health <= 0:
            respawn_x, respawn_y = 50, 50
            cursor.execute("""
                UPDATE bots
                SET health = 100, position_x = ?, position_y = ?
                WHERE bot_id = ?
            """, (respawn_x, respawn_y, target_user_id))
            drops = generate_drops()
            conn.commit()
            conn.close()
            return jsonify({
                'message': 'Bot died and respawned',
                'target': 'bot',
                'new_health': 100,
                'respawn_position': {'x': respawn_x, 'y': respawn_y},
                'drops': drops
            }), 200
        else:
            cursor.execute("UPDATE bots SET health = ? WHERE bot_id = ?", (new_health, target_user_id))
            conn.commit()
            conn.close()
            return jsonify({
                'message': 'Bot damaged',
                'target': 'bot',
                'new_health': new_health
            }), 200

    # fallback
    conn.close()
    return jsonify({'error': 'Unhandled target type'}), 400

def generate_drops():
    possible_drops = ["money", "apple", "blueberry", "Dark_Potion", "Life_Potion", "Fire_Potion", "Poison_Potion"]

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
                    conn.commit()
                    player_died = True
                    respawn_position = {'x': respawn_x, 'y': respawn_y}
                    player_health = 100
                else:
                    cursor.execute("UPDATE players SET health = ? WHERE player_id = ?", (new_health, player_id))
                    conn.commit()
                    player_health = new_health

                cursor.execute("UPDATE bots SET last_attack_time = ? WHERE bot_id = ?", (current_time, bot_id))
                conn.commit()

    # טיפול בפגיעות משחקנים אחרים
    cursor.execute("SELECT player_id, position_x, position_y, last_attack_time FROM players WHERE player_id != ?", (player_id,))
    other_players = cursor.fetchall()

    for p in other_players:
        other_id = p['player_id']
        other_x = p['position_x']
        other_y = p['position_y']
        last_attack = p['last_attack_time']

        if abs(other_x - player_x) < 100 and abs(other_y - player_y) < 100:
            try:
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
                        conn.commit()
                        player_died = True
                        respawn_position = {'x': respawn_x, 'y': respawn_y}
                        player_health = 100
                    else:
                        cursor.execute("UPDATE players SET health = ? WHERE player_id = ?", (new_health, player_id))
                        conn.commit()
                        player_health = new_health

                    cursor.execute("UPDATE players SET last_attack_time = ? WHERE player_id = ?", (current_time, other_id))
                    conn.commit()
            except:
                print("##################################################other_id",other_id)
    conn.close()

    response = {
        'was_attacked': was_attacked,
        'new_health': player_health
    }

    if player_died:
        response['respawn_position'] = respawn_position
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
    amount = data.get('amount', 1)  # default to 1

    if None in (object_name, has_space, player_id, slot_index):
        return jsonify({'error': 'Missing data'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Try to fetch the object from the map, but allow it to not exist
    cursor.execute("SELECT * FROM map_objects WHERE name = ?", (object_name,))
    obj = cursor.fetchone()

    if not has_space:
        conn.close()
        return jsonify({'success': False, 'message': 'No space in inventory'}), 200

    if object_name in ['tree', 'bush']:
        conn.close()
        return jsonify({'success': False, 'message': 'Object cannot be added to inventory'}), 200

    # Check if item already exists in inventory
    cursor.execute("""
        SELECT * FROM inventory
        WHERE player_id = ? AND name = ? AND slot_index = ?
    """, (player_id, object_name, slot_index))
    existing_item = cursor.fetchone()

    if existing_item:
        # Increase quantity
        cursor.execute("""
            UPDATE inventory
            SET quantity = quantity + ?
            WHERE inventory_id = ?
        """, (amount, existing_item['inventory_id']))
    else:
        # Insert new item
        cursor.execute("""
            INSERT INTO inventory (player_id, name, slot_index, quantity)
            VALUES (?, ?, ?, ?)
        """, (player_id, object_name, slot_index, amount))

    # If object existed on the map, delete it
    if obj:
        cursor.execute("DELETE FROM map_objects WHERE object_id = ?", (obj['object_id'],))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f'{object_name} added to inventory'}), 200
@app.route('/add_coin', methods=['POST'])
@token_required
def add_coin(user_id):
    """
    Add Coins to Player
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
            - amount
          properties:
            amount:
              type: integer
              example: 100
              description: Amount of coins to add
    responses:
      200:
        description: Coins successfully added
      400:
        description: Missing or invalid data
      401:
        description: Unauthorized
    """
    data = request.get_json()
    amount = data.get('amount')

    if not isinstance(amount, int) or amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Update player's currency
    cursor.execute("""
        UPDATE players SET currency = currency + ?
        WHERE player_id = ?
    """, (amount, user_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f'{amount} coins added to player {user_id}'}), 200

@app.route('/add_item', methods=['POST'])
@token_required
def add_item(user_id):
    """
    Add Item to Inventory via Drop
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
            - item_name
            - slot_index
            - has_space_in_inventory
          properties:
            item_name:
              type: string
              example: "Apple_Inventory"
              description: The name of the item to add to inventory
            slot_index:
              type: integer
              example: 1
              description: The index of the inventory slot
            has_space_in_inventory:
              type: boolean
              example: true
              description: Whether there is space for the item in inventory
    responses:
      200:
        description: Item successfully added or status returned
      400:
        description: Missing or invalid data
      401:
        description: Unauthorized
      404:
        description: Item not found on map
    """
    data = request.get_json()
    item_name = data.get('item_name')
    has_space = data.get('has_space_in_inventory')
    slot_index = data.get('slot_index')

    if None in (item_name, has_space, slot_index):
        return jsonify({'error': 'Missing data'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM map_objects WHERE name = ?
    """, (item_name,))
    obj = cursor.fetchone()

    if not obj:
        conn.close()
        return jsonify({'success': False, 'message': 'Item not found on map'}), 404

    if not has_space:
        conn.close()
        return jsonify({'success': False, 'message': 'No space in inventory'}), 200

    if obj['name'] in ['tree', 'bush']:
        conn.close()
        return jsonify({'success': False, 'message': 'Item cannot be added to inventory'}), 200

    cursor.execute("""
        SELECT * FROM inventory
        WHERE player_id = ? AND name = ? AND slot_index = ?
    """, (user_id, obj['name'], slot_index))
    existing_item = cursor.fetchone()

    if existing_item:
        cursor.execute("""
            UPDATE inventory
            SET quantity = quantity + 1
            WHERE inventory_id = ?
        """, (existing_item['inventory_id'],))
    else:
        cursor.execute("""
            INSERT INTO inventory (player_id, name, slot_index, quantity)
            VALUES (?, ?, ?, 1)
        """, (user_id, obj['name'], slot_index))

    cursor.execute("""
        DELETE FROM map_objects WHERE object_id = ?
    """, (obj['object_id'],))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f'{item_name} added to inventory'}), 200
@app.route('/drop_item_on_map', methods=['POST'])
@token_required
def drop_item_on_map(user_id):
    """
    Drop item on the map or add money directly
    """
    data = request.get_json()
    name = data.get("name")
    x = data.get("x")
    y = data.get("y")
    amount = data.get("amount")
    file = f"{name}.png"
    if not all([name, isinstance(x, (int, float)), isinstance(y, (int, float)), isinstance(amount, int)]):
        return jsonify({"error": "Invalid data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    if name.lower() == "money":
        # Update player currency
        cursor.execute("""
            UPDATE players SET coins = coins + ?
            WHERE player_id = ?
        """, (amount, user_id))
        message = f"{amount} coins added to player {user_id}"
        print("drop ,server 5")
    else:
        # Check if item already exists at same position
        cursor.execute("""
            SELECT COUNT(*) FROM map_objects
            WHERE name = ? AND position_x = ? AND position_y = ?
        """, (name, x, y))
        exists = cursor.fetchone()[0]

        if exists:
            message = f"{name} already exists at ({x}, {y}), not inserted again"
            print("drop ,server 6 - already exists")
        else:
            # Insert item on the map
            cursor.execute("""
                INSERT INTO map_objects (name, file, rotation, position_x, position_y)
                VALUES (?, ?, ?, ?, ?)
            """, (name, file, False, x, y))
            message = f"{name} x{amount} dropped at ({x}, {y})"
            print("drop ,server 6 - inserted")

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': message}), 200

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

@app.route('/get_inventory', methods=['GET'])
@token_required
def get_inventory(user_id):
    """
        Get the inventory state
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
    cursor.execute("""
        SELECT name, slot_index, quantity
        FROM inventory
        WHERE player_id = ?
        ORDER BY slot_index ASC
    """, (user_id,))
    inventory = cursor.fetchall()
    conn.close()

    items = [
        {
            "name": row["name"],
            "slot_index": row["slot_index"],
            "quantity": row["quantity"]
        }
        for row in inventory
    ]
    return jsonify({"inventory": items}), 200

@app.route('/remove_from_inventory', methods=['POST'])
@token_required
def remove_from_inventory(user_id):
    """
    Remove item from inventory
    ---
    tags:
      - Inventory
    consumes:
      - application/json
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: Bearer token for authentication
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            item_name:
              type: string
              example: Health Potion
            slot_index:
              type: integer
              example: 2
            amount:
              type: integer
              example: 1
    responses:
      200:
        description: Item successfully removed from inventory
      400:
        description: Item not found or does not match slot
      401:
        description: Unauthorized
    """
    data = request.get_json()
    item_name = data.get('item_name')
    slot_index = data.get('slot_index')
    amount = data.get('amount', 1)  # ברירת מחדל: 1

    if not item_name or slot_index is None:
        return jsonify({'error': 'Missing item_name or slot_index'}), 400

    if not isinstance(amount, int) or amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # שליפת הפריט מהמלאי
    cursor.execute("""
        SELECT * FROM inventory
        WHERE player_id = ? AND slot_index = ?
    """, (user_id, slot_index))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return jsonify({'error': 'No item found in that slot'}), 400

    if row['name'] != item_name:
        conn.close()
        return jsonify({'error': f"Item in slot {slot_index} is '{row['name']}', not '{item_name}'"}), 400

    if row['quantity'] > amount:
        # רק מפחיתים מהכמות
        cursor.execute("""
            UPDATE inventory
            SET quantity = quantity - ?
            WHERE inventory_id = ?
        """, (amount, row['inventory_id']))
    else:
        # מוחקים את כל השורה אם הכמות קטנה או שווה
        cursor.execute("""
            DELETE FROM inventory
            WHERE inventory_id = ?
        """, (row['inventory_id'],))

    conn.commit()
    conn.close()

    return jsonify({'message': f'{amount} of {item_name} removed'}), 200

@app.route('/respawn', methods=['POST'])
@token_required
def respawn(user_id):
    conn = sqlite3.connect('DATABASE_GAME.db')
    c = conn.cursor()

    # Get current health
    c.execute('SELECT health FROM players WHERE id = ?', (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Player not found'}), 404

    health = row[0]
    if health > 0:
        conn.close()
        return jsonify({'message': 'Player is still alive'}), 400

    # Respawn at a random location (adjust range as needed)
    new_x = random.randint(100, 800)
    new_y = random.randint(100, 600)
    new_health = 100

    # Update player
    c.execute('UPDATE players SET position_x = ?, position_y = ?, health = ? WHERE id = ?',
              (new_x, new_y, new_health, user_id))
    conn.commit()
    conn.close()

    return jsonify({
        'message': 'Player respawned',
        'new_position': {'x': new_x, 'y': new_y},
        'health': new_health
    }), 200

class lbconector:
    def __init__(self):
        self.lBaddr = ()
    def ipSender(self,udp_port, flask_port):
        global ip, portLb
        BUFFER_SIZE = 1024
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            server_socket.bind(("", udp_port))
        except OSError as e:
            return

        while True:
            data, addr = server_socket.recvfrom(BUFFER_SIZE)
            print(f"Received from {addr}: {data.decode()}")
            decoded = data.decode(errors='ignore')
            if data.decode().lower()[0] == "r":
                response = f"1|{flask_port}".encode()  # Safer format
                server_socket.sendto(response, addr)
                portLb = int(data.decode().lower()[1:])
            elif decoded[0] == "u":
                print("hi")
                self.save_player_data(decoded[1:])

    def save_player_data(self, player_data, db_path='../DATABASE_GAME.db'):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        player_data = json.loads(player_data)
        print(player_data)
        # Upsert player data
        c.execute("""
            INSERT INTO players (player_id, username, password_hash, position_x, position_y, health, coins, status, speed, last_attack_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(player_id) DO UPDATE SET
                username = excluded.username,
                password_hash = excluded.password_hash,
                position_x = excluded.position_x,
                position_y = excluded.position_y,
                health = excluded.health,
                coins = excluded.coins,
                status = excluded.status,
                speed = excluded.speed,
                last_attack_time = excluded.last_attack_time
        """, (
            player_data["player_id"],
            player_data["username"],
            player_data["password_hash"],
            player_data["position_x"],
            player_data["position_y"],
            player_data["health"],
            player_data["coins"],
            player_data["status"],
            player_data["speed"],
            player_data["last_attack_time"]
        ))

        # Replace inventory
        c.execute("DELETE FROM inventory WHERE player_id = ?", (player_data["player_id"],))
        for item in player_data.get("inventory", []):
            c.execute("""
                INSERT INTO inventory (player_id, name, slot_index, quantity)
                VALUES (?, ?, ?, ?)
            """, (player_data["player_id"], item["name"], item["slot_index"], item["quantity"]))

        conn.commit()
        conn.close()

    def send_player_data(self,username, db_path='../DATABASE_GAME.db'):
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # Query player by username
        c.execute("SELECT * FROM players WHERE username = ?", (username,))
        row = c.fetchone()

        conn.close()

        if row:
            # Convert row to dict
            player_data = {
                "player_id": row[0],
                "username": row[1],
                "password_hash": row[2],
                "position_x": row[3],
                "position_y": row[4],
                "health": row[5],
                "coins": row[6],
                "status": row[7],
                "speed": row[8],
                "last_attack_time": row[9]
            }
            c.execute("SELECT name, quantity, slot_index FROM inventory WHERE player_id = ?", (row[0],))
            inventory = [{"name": item[0], "quantity": item[1], "slot_index": item[2]} for item in c.fetchall()]
            player_data["inventory"] = inventory
            # Send back over UDP
            data =findy.main()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = b"u" + json.dumps(player_data, default=str).encode()
            sock.sendto(message, data['lb'])
            sock.close()
        else:
            pass

    def PortDefinder(self,start_port):
        port = start_port
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                if sock.connect_ex(('localhost', port)) != 0:
                    return port
            port += 1

    def run(self,port):
        app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    lb = lbconector()
    flask_port = lb.PortDefinder(5150)
    udp_port = lb.PortDefinder(flask_port + 1)

    print(f"Flask Port: {flask_port}, UDP Port: {udp_port}")
    t1 = threading.Thread(target=lb.ipSender, args=(udp_port, flask_port))
    t2 = threading.Thread(target=lb.run, args=(flask_port,))
    t3 = threading.Thread(target=move_bots, args=())
    t2.start()
    t1.start()
    t3.start()
