import json
import random

def generate_mobs(count, screens_x=40, screens_y=40, screen_width=1920, screen_height=1080, used_positions=None):
    mobs = {}
    used_positions = used_positions or set()

    for i in range(count):
        while True:
            screen_x = random.randint(0, screens_x - 1)
            screen_y = random.randint(0, screens_y - 1)

            pixel_x = screen_x * screen_width + random.randint(0, screen_width - 1)
            pixel_y = screen_y * screen_height + random.randint(0, screen_height - 1)

            pose = f"{pixel_x},{pixel_y}"
            if pose not in used_positions:
                used_positions.add(pose)
                break

        mobs[str(i)] = {
            "pose": pose,
            "type": random.choice(["a", "b", "c"])
        }

    return mobs

# Use the same file for both reading and writing
filename = "ips.json"

# Load existing file
with open(filename, "r") as f:
    data = json.load(f)

# Move mob out of players if needed
if "mob" in data.get("players", {}):
    del data["players"]["mob"]

# Gather used positions from players
used_positions = {p["pose"] for p in data.get("players", {}).values()}

# Add mob section
data["mob"] = generate_mobs(count=1, used_positions=used_positions)

# Save back to the same file
with open(filename, "w") as f:
    json.dump(data, f, indent=2)

print("✅ Fixed structure and added mobs to ips.json.")
