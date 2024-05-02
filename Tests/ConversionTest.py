import math

def decToKey(num):
        charNum = 0
        key = ""
        for i in range(keyLen):
            remKey = num % 26
            num = math.floor(num/26)
            key += chr(remKey + asciiBase)
        return key

def keyToDec(key):
    #Turn key into char list
    keyList = list(key)
    keyValue = 0
    for i in range(len(keyList)):
        #convert chars to ascii; shift so that A = 1, B = 2, etc
        num = ord(keyList[i]) - asciiBase
        #convert shifted ascii to base 26 counting
        keyValue += num*(26**i)
    return keyValue

def incrementKey(key):
    key = list(key)
    for i in range(len(key)):
        if(key[i] != 'Z'):
            key[i] = chr(ord(key[i])+1)
            break
        else:
            key[i] = 'A'
            continue
    return "".join(key)

key = "AAAA"
keyLen = 4
asciiBase = ord('A')

for i in range(26**4):
    keyVal = keyToDec(key)
    #print("Expected Key: " + key)
    #print("Decimal: " + str(keyVal))
    keyRet = decToKey(keyVal)
    #print("Key: " + keyRet)
    if(keyRet != key):
        print("Test Failed")
        break
    key = incrementKey(key)
print("Test Success")