import fixedHomeScreen
import game1
suffix = fixedHomeScreen.main('192.168.1.79', 8827).decode().strip()
ip = f'192.168.{suffix[2:]}'
print(ip)
game1.main(ip)
