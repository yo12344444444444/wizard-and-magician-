import random

def object_place():
    x = random.randrange(0, 48000)             #x equals a random number between the numbers 0 and 48000 (the length of the screen)
    print(x)
    y = random.randrange(0, 32000)             #y equals a random number between the numbers 0 and 32000 (the height of the screen)
    print(y)

object_place()
