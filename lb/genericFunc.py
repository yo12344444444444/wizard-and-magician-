import sqlite3
import findy
import socket
import threading

class Servers:
    def __init__(self):
        self.servers = {}
        # Connect to (or create) the database
        self.conn = sqlite3.connect('servers_info.db')
        self.c = self.conn.cursor()

        # Create tables for servers and people if they don't exist
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            server TEXT PRIMARY KEY,
            ip TEXT NOT NULL,
            port INTEGER DEFAULT 0
        )
        ''')
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS people (
            username TEXT PRIMARY KEY,
            ip TEXT NOT NULL,
            port INTEGER DEFAULT 0
        )
        ''')

        # Get server information from findy
        ss = findy.main()  # Assuming findy.main() returns a list of tuples with (ip, port, server_name)
        for i in ss:
            self.servers[i[1]] = i[0]  # Assumes i[1] is server_name and i[0] is the (ip, port)

        # Insert servers into database
        for server, (ip, port) in self.servers.items():
            self.c.execute('''
            INSERT OR REPLACE INTO servers (server, ip, port)
            VALUES (?, ?, ?)
            ''', (server, ip, port))

        # Commit changes and close database connection
        self.conn.commit()

    # Method to get a player (client) connection on a free port
    def get_player(self):
        for port in range(5000, 6000):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("0.0.0.0", port))
                s.listen()
                print(f"Listening on port {port}")
                break
            except OSError:
                s.close()
                continue
        else:
            print("No free port found.")
            return None

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connection from {addr} on port {port}")
                data = conn.recv(1024)
                if data:
                    print(f"Received: {data.decode(errors='ignore')}")

                    conn.sendall(b"hi buck")

    # Close the database connection
    def close_connection(self):
        self.conn.close()
