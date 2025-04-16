from flask import Flask, request, jsonify
import sqlite3
from jose import jwt  # Replace PyJWT with jose.jwt
import datetime
from functools import wraps
from flasgger import Swagger
import time

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
            schema:
              type: object
              properties:
                players:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                      x:
                        type: integer
                      y:
                        type: integer
                bots:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                      x:
                        type: integer
                      y:
                        type: integer
                objects:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                      x:
                        type: integer
                      y:
                        type: integer
          401:
            description: Unauthorized - token missing or invalid
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Invalid or expired token
        """
    data = request.get_json()
    screen_width = data.get('screen_width')
    screen_height = data.get('screen_height')
    return get_game_state(user_id, screen_width, screen_height)


def get_game_state(user_id,screen_width,screen_height):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM players WHERE player_id = ?", (user_id,))
    main_player = cursor.fetchone()
    if not main_player:
        conn.close()
        return jsonify({'error': 'Player not found'}), 404

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
    return jsonify({
        'players': players,
        'bots': bots,
        'objects': objects
    })


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
    move_amount = 1

    if direction not in ['w', 'a', 's', 'd']:
        return jsonify({'error': 'Invalid direction'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT position_x, position_y FROM players WHERE player_id = ?", (user_id,))
    player = cursor.fetchone()

    if not player:
        conn.close()
        return jsonify({'error': 'Player not found'}), 404

    x, y = player['position_x'], player['position_y']

    if direction == 'w':
        y -= move_amount
    elif direction == 's':
        y += move_amount
    elif direction == 'a':
        x -= move_amount
    elif direction == 'd':
        x += move_amount

    cursor.execute("UPDATE players SET position_x = ?, position_y = ? WHERE player_id = ?", (x, y, user_id))
    conn.commit()
    conn.close()

    response = get_game_state(user_id, screen_width, screen_height)
    return response

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

        # קביעת נזק לפי סוג נשק
        weapon_damage = {
            'Stone_Sword': 10,
            'Iron_Sword': 15,
            'Gold_Sword': 20,
            'Wood_Wand': 10,
            'Gold_Wand': 20
        }
        damage = weapon_damage.get(weapon_type, 5)  # ברירת מחדל

        conn = get_db_connection()
        cursor = conn.cursor()

        if target_type == 'player':
            cursor.execute("SELECT health FROM players WHERE player_id = ?", (target_user_id,))
            player = cursor.fetchone()

            if player:
                new_health = player['health'] - damage

                if new_health <= 0:
                    # שחקן מת – מאפסים אותו
                    cursor.execute("""
                        UPDATE players
                        SET health = ?, position_x = ?, position_y = ?, coins = 0
                        WHERE player_id = ?
                    """, (100, 50, 50,target_user_id))
                    conn.commit()
                    conn.close()
                    return jsonify({'message': 'Player died and respawned', 'target': 'player'}), 200

                else:
                    cursor.execute("UPDATE players SET health = ? WHERE player_id = ?",
                                   (new_health, target_user_id))
                    conn.commit()
                    conn.close()
                    return jsonify({'message': 'Player damaged', 'new_health': new_health, 'target': 'player'}), 200

            conn.close()
            return jsonify({'error': 'Player not found'}), 404

        elif target_type == 'bot':
            cursor.execute("SELECT health FROM bots WHERE bot_id = ?", (target_user_id,))
            bot = cursor.fetchone()

            if bot:
                new_health = bot['health'] - damage
                print('new_health',new_health)
                if new_health <= 0:
                    cursor.execute("""UPDATE bots
                        SET health = ?, position_x = ?, position_y = ?
                        WHERE bot_id = ?
                    """, (100, 50, 50, target_user_id))
                    conn.commit()
                    conn.close()
                    return jsonify({'message': 'bot died and respawned', 'target': 'player'}), 200
                else:
                    cursor.execute("UPDATE bots SET health = ? WHERE bot_id = ?", (new_health, target_user_id))
                    conn.commit()
                    conn.close()
                    return jsonify({'message': 'Bot damaged', 'new_health': new_health, 'target': 'bot'}), 200

            conn.close()
            return jsonify({'error': 'Bot not found'}), 404

    return jsonify({'collision': False}), 200

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

    # קבלת הבוטים
    cursor.execute("SELECT bot_id, position_x, position_y, last_attack_time FROM bots")
    bots = cursor.fetchall()

    current_time = int(time.time())
    was_attacked = False

    for bot in bots:
        bot_id = bot['bot_id']
        bot_x = bot['position_x']
        bot_y = bot['position_y']
        last_attack = bot['last_attack_time']

        # בדיקה אם הבוט בטווח פגיעה (נניח טווח של 100 פיקסלים)
        if abs(bot_x - player_x) < 100 and abs(bot_y - player_y) < 100:
            # האם עברו לפחות 5 שניות מהתקיפה האחרונה?
            if current_time - last_attack >= 5:
                # תקיפה! מורידים 10 חיים לשחקן
                new_health = max(player_health - 10, 0)
                cursor.execute("UPDATE players SET health = ? WHERE player_id = ?", (new_health, player_id))
                cursor.execute("UPDATE bots SET last_attack_time = ? WHERE bot_id = ?", (current_time, bot_id))
                player_health = new_health  # לעדכון בתקיפה חוזרת עם כמה בוטים
                was_attacked = True

    conn.commit()
    conn.close()

    return {'was_attacked': was_attacked}
@app.route('/check-object', methods=['POST'])
def check_object():
    """
    בדיקת אובייקט לפי מיקום
    ---
    tags:
      - Game
    consumes:
      - application/json
    parameters:
      - in: body
        name: coordinates
        required: true
        schema:
          type: object
          required:
            - x
            - y
          properties:
            x:
              type: integer
              example: 100
            y:
              type: integer
              example: 200
    responses:
      200:
        description: נמצא אובייקט
      404:
        description: לא נמצא אובייקט
    """
    data = request.get_json()
    x = data.get('x')
    y = data.get('y')

    if x is None or y is None:
        return jsonify({'error': 'Missing coordinates'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT code, file FROM map_objects WHERE position_x = ? AND position_y = ?
    """, (x, y))
    obj = cursor.fetchone()
    conn.close()

    if obj:
        return jsonify({
            'found': True,
            'code': obj['code'],
            'file': obj['file']
        }), 200
    else:
        return jsonify({'found': False}), 404

@app.route('/add-to-inventory', methods=['POST'])
def add_to_inventory():
    """
    הוספת חפץ לאינבנטורי אם יש מקום והוא אינו tree או bush
    ---
    tags:
      - Game
    consumes:
      - application/json
    parameters:
      - in: body
        name: data
        required: true
        schema:
          type: object
          required:
            - object_name
            - player_id
            - slot_index
            - has_space_in_inventory
          properties:
            object_name:
              type: string
              example: "potion_red"
            player_id:
              type: integer
              example: 1
            slot_index:
              type: integer
              example: 3
            has_space_in_inventory:
              type: boolean
              example: true
    responses:
      200:
        description: תוצאת ניסיון ההוספה לאינבנטורי
    """
    data = request.get_json()
    object_name = data.get('object_name')
    has_space = data.get('has_space_in_inventory')
    player_id = data.get('player_id')
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

    if obj['code'] in ['tree', 'bush']:
        conn.close()
        return jsonify({'success': False, 'message': 'Object cannot be added to inventory'}), 200

    # בדיקה אם האובייקט כבר קיים בתא הזה של השחקן
    cursor.execute("""
        SELECT * FROM inventory
        WHERE player_id = ? AND name = ? AND slot_index = ?
    """, (player_id, obj['code'], slot_index))
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
        """, (player_id, obj['code'], slot_index))

    # הסרה מהמפה
    cursor.execute("""
        DELETE FROM map_objects WHERE object_id = ?
    """, (obj['object_id'],))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f'{object_name} added to inventory'}), 200

if __name__ == '__main__':
    app.run(debug=True)
