import sqlite3
import findy
import socket
import threading




class Servers:
    def get_player(self,port, p):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("0.0.0.0", port))
        print(f"Listening for UDP on port {port}")

        while True:
            data, addr = s.recvfrom(1024)
            #print(f"Received from {addr}: {data.decode(errors='ignore')}")
            msg = "lb"+str(p)
            if data.decode(errors='ignore') == "r":
                s.sendto(msg.encode(), addr)
            elif data.decode(errors='ignore') == "p":
                sendDb()
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
    # Close the database connection
    def close_connection(self):
        self.conn.close()
