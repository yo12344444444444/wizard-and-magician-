import fixedHomeScreen
from server import Game2
token = fixedHomeScreen.main('127.0.0.1', 8827)
ip = '127.0.0.1'
print(ip)
Game2.main(token)
print("end")
