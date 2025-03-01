import json

with open("ips.json", "r") as f:
    y = json.load(f)

print(json.dumps(y, indent=4))  # Pretty-print the file content
