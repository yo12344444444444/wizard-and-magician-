from flask import Flask, request, jsonify
import sqlite3
from jose import jwt  # Replace PyJWT with jose.jwt
import datetime
from functools import wraps

app = Flask(__name__)
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE players SET status = 'inactive' WHERE player_id = ?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User logged out successfully'})

@app.route('/get_player', methods=['GET'])
@token_required
def get_player(user_id):
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
    data = request.get_json()
    screen_width = data.get('x')
    screen_height = data.get('y')

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

if __name__ == '__main__':
    app.run(debug=True)
