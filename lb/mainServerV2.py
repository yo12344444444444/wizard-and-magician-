import sqlite3
import findy

# Connect to (or create) the database
conn = sqlite3.connect('/app/database/servers_info.db')
c = conn.cursor()

# Create table: server name, IP, port, and people count
c.execute('''
CREATE TABLE IF NOT EXISTS servers (
    server TEXT PRIMARY KEY,
    ip TEXT NOT NULL,
    port INTEGER DEFAULT 0,
    people INTEGER DEFAULT 0
)
''')

# Get server information from findy
# findy.main() should return a tuple: ((ip, port), numServer)
(ip, port), num_server = findy.main()

# Servers and their IPs (you can modify if needed)
servers = {
    'server1': '192.168.1.10',
    'server2': '192.168.1.11',
    'server3': '192.168.1.12',
    'server4': '192.168.1.13'
}

# Insert servers into database
for server, ip_address in servers.items():
    c.execute('''
    INSERT OR REPLACE INTO servers (server, ip, port, people)
    VALUES (?, ?, ?, ?)
    ''', (server, ip_address, port, 0))  # starting with 0 people

# Save and close
conn.commit()
conn.close()
