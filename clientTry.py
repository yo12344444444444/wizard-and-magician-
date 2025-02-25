import json

with open("ips.json", "r") as f:
    y = json.load(f)
    print('10.100.102.2' in y["plyers"])
for a in y["plyers"]:
    if '10.100.102.2' not in a:
        print(a)
