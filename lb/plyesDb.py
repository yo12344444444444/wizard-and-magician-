from flask import Flask, request, jsonify
import sqlite3
from jose import jwt
import datetime
from functools import wraps
from flasgger import Swagger
import os

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

DATABASE = '/app/database/servers_info.db'

# ✅ Create the database and players table if they don't exist
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Check if 'players' table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players'")
    table_exists = c.fetchone()

    if not table_exists:
        c.execute('''
            CREATE TABLE players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                server INTEGER NOT NULL
            )
        ''')
    else:
        # Check if 'server' column exists
        c.execute("PRAGMA table_info(players)")
        columns = [row[1] for row in c.fetchall()]
        if 'server' not in columns:
            c.execute("ALTER TABLE players ADD COLUMN server INTEGER NOT NULL DEFAULT 0")
        else:
            print("Database and table already exist with correct schema.")

    conn.commit()
    conn.close()

def add_test_user():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Drop the players table if it already exists
    c.execute("DROP TABLE IF EXISTS players")

    # Recreate the players table with the correct schema
    c.execute('''
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            server INTEGER NOT NULL
        )
    ''')

    # Insert the test user
    try:
        c.execute("INSERT INTO players (username, password, server) VALUES (?, ?, ?)", ("2212", "2212", 2))
        conn.commit()
    except sqlite3.IntegrityError:
        print("errer")
    conn.close()

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
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO players (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    finally:
        conn.close()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE username = ? AND password = ?", (username, password))
    user = cur.fetchone()
    conn.close()

    if user:
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/player', methods=['GET'])
@token_required
def get_player(user_id):
    server_id = request.args.get('server')  # Optionally, retrieve server from query params
    conn = get_db_connection()
    cur = conn.cursor()
    if server_id:
        cur.execute("SELECT id, username, server FROM players WHERE id = ? AND server = ?", (user_id, server_id))
    else:
        cur.execute("SELECT id, username, server FROM players WHERE id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    if user:
        return jsonify({'id': user['id'], 'username': user['username'], 'server': user['server']})
    else:
        return jsonify({'error': 'User not found'}), 404

app.run(host='0.0.0.0', port=5005, debug=False)
