import random
import json
from typing import TextIO

print('start')
count = 0
typeOfObject = "a"

print('befor open')
inputFile = open(r'location.json', 'a')     #the place of the file
print('after open')
while typeOfObject < "n":
    x = random.randrange(0, 48000)
    y = random.randrange(0, 32000)
    location = {
      "objectType": typeOfObject,
      "objectID": 2,
      "x": x,
      "y": y
    }
    print('befor write')
    while count < 500:
        inputFile.write(json.dumps(location))
        print("after write")
        count = count + 1
    count = 0
    typeOfObject = chr(ord(typeOfObject)+1)
    print('after typeOfObject + 1////////////////////////////////////////////////////////////////////////' + typeOfObject)


