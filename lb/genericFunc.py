import sqlite3
from findy import findy
import socket
import threading
import json


class Servers:
    def send_player_data(self, addr, username, db_path='../DATABASE_GAME.db'):
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

            # Send back over UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = b"u" + json.dumps(player_data, default=str).encode()
            sock.sendto(message, addr)
            sock.close()
            print(f"Sent player data for '{username}' to {addr}")
        else:
            print(f"Username '{username}' not found in local database.")

    def get_player(self, port, p):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("0.0.0.0", port))
        while True:
            data, addr = s.recvfrom(1024)
            msg = "lb|" + str(p)
            print(msg, )
            decoded = data.decode(errors='ignore')
            if decoded[0] == "r":
                s.sendto(msg.encode(), addr)
            elif decoded[0] == "p":
                pass
            elif decoded[0] == "u":
                json_data = decoded[1:]
                self.save_player_data(json_data)

    def save_player_data(self, player_data, db_path='../DATABASE_GAME2.db'):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        player_data = json.loads(player_data)
        # Upsert by player_id
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
        for item in player_data.get("inventory", []):
            c.execute("""
                INSERT INTO inventory (player_id, name, slot_index, quantity)
                VALUES (?, ?, ?, ?)
            """, (player_data["player_id"], item["name"], item["slot_index"], item["quantity"]))
        conn.commit()
        conn.close()

    def init_player_table(self, db_path='../DATABASE_GAME2.db'):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS players (
                player_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                position_x INTEGER,
                position_y INTEGER,
                health INTEGER,
                coins INTEGER,
                status TEXT,
                speed INTEGER,
                last_attack_time TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def __init__(self, port):
        self.servers = {}
        self.port = port
        # Connect to the database
        self.conn = sqlite3.connect('../DATABASE_GAME2.db', check_same_thread=False)
        self.c = self.conn.cursor()
        self.init_player_table()
        # Create tables
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            server TEXT PRIMARY KEY,
            ip TEXT NOT NULL,
            port INTEGER DEFAULT 0
        )''')
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS people (
            username TEXT PRIMARY KEY,
            ip TEXT NOT NULL,
            port INTEGER DEFAULT 0
        )''')
        finder = findy()
        # Load servers from findy
        while True:
            self.servers = finder.main(self.port)
            if len(self.servers) == 1:
                break
        # Insert into DB
        for server, (ip, port) in self.servers.items():
            self.c.execute('''
            INSERT OR REPLACE INTO servers (server, ip, port)
            VALUES (?, ?, ?)''', (server, ip, port))

        self.conn.commit()

    def sendDb(self, addr, username, db_path='../DATABASE_GAME2.db'):
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
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            message = json.dumps(player_data, default=str).encode()
            sock.sendto(message, addr)
            sock.close()
        else:
            pass

    def close_connection(self):
        self.conn.close()
