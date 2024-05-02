import math

def decToKey(num):
    """Convert decimal number to a key"""
    charNum = 0
    key = ""
    for i in range(keyLen):
        remKey = num % base
        num = math.floor(num/base)
        key += keyLetters[remKey]
    return key

def keyToDec(key):
    """Convert key to a decimal number"""
    #Turn key into char list
    keyList = list(key)
    keyValue = 0
    for i in range(len(keyList)):
        #convert chars to numbers
        num = keyLetters.index(keyList[i])
        #convert shifted ascii to base 26 counting
        keyValue += num*(base**i)
    return keyValue

key = 0
keyLen = 4
keyLetters = ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Z']
base = 20

for i in range(base**keyLen):
    keyVal = decToKey(key)
    print("Key: " + str(keyVal))
    keyRet = keyToDec(keyVal)
    print("Dec: " + str(keyRet))
    print("Expected Dec: " + str(key))
    if(keyRet != key):
        print("Test Failed")
        break
    key += 1
print("Test Success")