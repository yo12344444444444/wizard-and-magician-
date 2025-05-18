import socket
from collections import Counter

from genericFunc import Servers
from flask import Flask, request, jsonify
import sqlite3
from jose import jwt
import datetime
from functools import wraps
from flasgger import Swagger
import threading


DATABASE = '/app/database/DATABASE_GAME2.db'


def ggeter(port):
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

    def get_db_connection():
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token or not token.startswith("Bearer "):
                return jsonify({'error': 'Token is missing or invalid format!'}), 403
            try:
                data = jwt.decode(token[7:], app.config['SECRET_KEY'], algorithms=['HS256'])
                user_id = data['user_id']
            except jwt.JWTError as e:
                return jsonify({'error': 'Token is invalid or expired!'}), 403
            return f(user_id=user_id, *args, **kwargs)

        return decorated

    @app.route('/')
    def index():
        return jsonify({'message': 'Game API is running'})


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
        print("lol")
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'User already exists'}), 400
        # Create new user
        cursor.execute("""
            INSERT INTO players (username,server, password_hash, position_x, position_y, health, coins, status, speed, last_attack_time)
        VALUES (?,?, ?, 0, 100, 100, 100, 'active', 3 ,1)
        """,
        (username,get_least_loaded_server(), password))
        player_id = cursor.lastrowid
        print(get_least_loaded_server())
        # Add starter items to inventory
        starter_items = [
            ('Wood_Wand', 1),
            ('Stone_Sword', 2)
        ]
        for name, slot_index in starter_items:
            print(slot_index)
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
        s.sendDb(get_least_loaded_server(),username=user['username'])
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
            s.sendDb(user['server'], user['username'])
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

    @app.route('/get_player', methods=['GET'])
    @token_required
    def get_player(user_id):
        server_id = request.args.get('server')  # Optionally, retrieve server from query params
        conn = get_db_connection()
        cur = conn.cursor()
        if server_id:
            cur.execute("SELECT id, username, server FROM players WHERE id = ? AND server = ?", (user_id, server_id))
        else:
            cur.execute("SELECT player_id, username, server FROM players WHERE player_id = ?", (user_id,))
        user = cur.fetchone()
        conn.close()
        if user:
            print("server", user['server'])
            s.sendDb(user['server'], user['username'])
            return jsonify({'id': user['player_id'], 'username': user['username'], 'server': user['server']})
        else:
            return jsonify({'error': 'User not found'}), 404

    app.run(host='0.0.0.0', port=port, debug=False)

def get_least_loaded_server(db_path='/app/database/DATABASE_GAME2.db'):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get all server entries
    try:
        cur.execute("SELECT server FROM players")
    except:
        return 1
    servers = [row[0] for row in cur.fetchall() if row[0] is not None]
    servers += {'1':0}
    conn.close()

    if not servers:
        return 1  # No players or servers found

    # Count number of players per server
    server_counts = Counter(servers)

    # Return server with minimum players
    if min(server_counts, key=server_counts.get) is not None:
        return min(server_counts, key=server_counts.get)
    else:
        return 1

def PortDefinder(port):
    port = port
    result = 0
    while result == 0:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('localhost', port))
        if result == 0:
            port += 1
    return port


def add_test_user():
    return -1
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Drop the players table if it already exists

    # Recreate the players table with the correct schema


    # Insert the test user
    try:
        """:c.execute("INSERT INTO players (username, password_hash, position_x, position_y, health, coins, status)
        VALUES (2212, 2212, 0, 100, 100, 100, 'active'))"""
        conn.commit()
    except sqlite3.IntegrityError:
        print("errer")
    conn.close()


add_test_user()
port = PortDefinder(5000)
p = PortDefinder(port + 2)
s = Servers(p)
print(p, port)
t1 = threading.Thread(target=ggeter, args=(port,))
t1.start()
t2 = threading.Thread(target=s.get_player, args=(p, port,))

t2.start()
