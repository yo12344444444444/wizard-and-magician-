import sqlite3
import findy
import socket
import threading
import json


class Servers:
    def get_player(self, port, p):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("0.0.0.0", port))
        print(f"Listening for UDP on port {port}")

        while True:
            data, addr = s.recvfrom(1024)
            msg = "lb" + str(p)
            decoded = data.decode(errors='ignore')

            if decoded == "r":
                s.sendto(msg.encode(), addr)
            elif decoded == "p":
                db_data = self.sendDb()
                s.sendto(db_data.encode(), addr)

    def __init__(self):
        self.servers = {}

        # Connect to the database
        self.conn = sqlite3.connect('../DATABASE_GAME.db', check_same_thread=False)
        self.c = self.conn.cursor()

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

        # Load servers from findy
        ss = findy.main()  # Returns list of (ip, port, server_name)
        for ip, port, server in ss:
            self.servers[server] = (ip, port)

        # Insert into DB
        for server, (ip, port) in self.servers.items():
            self.c.execute('''
            INSERT OR REPLACE INTO servers (server, ip, port)
            VALUES (?, ?, ?)''', (server, ip, port))

        self.conn.commit()

    def sendDb(self):
        print("hii")
        # Returns JSON string of all tables including players
        db_dump = {"servers": [], "people": [], "players": []}

        for row in self.c.execute("SELECT * FROM servers"):
            db_dump["servers"].append({"server": row[0], "ip": row[1], "port": row[2]})

        for row in self.c.execute("SELECT * FROM people"):
            db_dump["people"].append({"username": row[0], "ip": row[1], "port": row[2]})

        for row in self.c.execute("SELECT * FROM players"):
            db_dump["players"].append({
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
            })

        return json.dumps(db_dump, default=str)  # default=str to handle datetime

    def close_connection(self):
        self.conn.close()


if __name__ == "__main__":
    s = Servers()
    threading.Thread(target=s.get_player, args=(9999, 42), daemon=True).start()

    input("Press Enter to stop...\n")
    s.close_connection()
