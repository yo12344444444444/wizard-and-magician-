CREATE TABLE players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT UNIQUE NOT NULL,
    pose_x INTEGER NOT NULL,
    pose_y INTEGER NOT NULL,
    money INTEGER DEFAULT 200,
    health INTEGER DEFAULT 100 --the amount of health that the players start with
);

CREATE TABLE items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

INSERT INTO players (ip_address, pose_x, pose_y, money, health) VALUES
('10.100.102.2', 21600, 38400, 200, 100),
('10.100.102.3', 21600, 38400, 200, 100);

INSERT INTO items (player_id, item_name, quantity) VALUES
(1, 'Sword', 1),
(1, 'HealthPotion', 3),
(2, 'Bow', 1);
