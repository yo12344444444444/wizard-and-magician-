import sqlite3
import findy

# Connect to (or create) the database
conn = sqlite3.connect('servers_info.db')
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
ss = findy.main()
servers = {}
for i in ss:
    servers[i[1]] = i[0]
port =0
# Servers and their IPs (you can modify if needed)
def getPlyear():

    return None #rutern (ip,port)
# Insert servers into database
for server, ip_address in servers.items():
    c.execute('''
    INSERT OR REPLACE INTO servers (server, ip, port, people)
    VALUES (?, ?, ?, ?)
    ''', (server, ip_address[0], ip_address[1], 0))  # starting with 0 people

# Save and close
conn.commit()
conn.close()
