#UniqueKeyTest.py  Copyright (C) 2024  Valparaiso University

import math
from pathlib import Path
import numpy
import os
from FrontendPackage import KeyGenerator

keyGen = KeyGenerator("keyList.txt")
keysUsed = Path("keyUsed.txt")
keysList = Path("keyList.txt")
#Create keys used file
usedFile = open(keysUsed, "w")
usedFile.write("")
usedFile.close()

while True:
    #Get a new key
    key = keyGen.getNextKey()
    if(key == 0):
        print("Test Success: All keys used; None reused")
        break
    #Check if key is inside used keys file
    usedFile = open(keysUsed, "r")
    usedlist = usedFile.read().split('\n')
    for i in range(len(usedlist)):
        if(key == usedlist[i]):
            print("Test Failed: Key reused")
            break
    usedFile.close()
    #Update used keys list
    usedFile = open(keysUsed, "a")
    usedFile.write(key + "\n")
    usedFile.close()

os.remove(keysUsed)
os.remove(keysList)
