import math
from pathlib import Path
import numpy
import os

class KeyGenerator:
    def __init__(self, filename):
        #Initialize key
        self.key = None
        #Array containing possible letters
        #No vowels/y ensures that no profanity will be generated for the key
        self.keyLetters = ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Z']
        self.countBase = len(self.keyLetters)
        #Set file name
        self.filename = filename
        #Set key length
        self.keyLen = 4
        #Create text file containing key codes
        self.__createFile()

    def getNextKey(self):
        keyCode, updatedList = self.__getKeyCode()
        self.__updateFile(updatedList)
        self.key = self.__decToKey(keyCode)
        return self.key
        
    def addKey(self, key):
        #Open file in append mode
        keyFile = open(self.filename, "a")
        #Append decimal representation of key to file
        keyFile.write(str(self.__keyToDec(str(key))) + "\n")
        keyFile.close()
    
    def __getKeyCode(self):
        #Open file
        keyFile = open(self.filename, "r")
        #Check if any keys left
        if(not keyFile.read(1)):
            #Add length and generate file again
            keyLen+=1
            self.__createFile()
        #Read keys into list
        keylist = keyFile.read().split('\n')
        keyFile.close()
        #Remove any blank entries and convert to numpy array
        keylist = numpy.array(list(filter(None, keylist)))
        keyCode = numpy.random.choice(keylist)
        updatedList = numpy.delete(keylist, numpy.where(keylist==keyCode))
        print(keyCode)
        return int(keyCode), updatedList
            
    def __updateFile(self, keyArr):
        #Clear keyFile
        keyFile = open(self.filename, "w")
        keyFile.write("")
        keyFile.close()
        #Write keys to keyFile
        keyFile = open(self.filename, "a")
        for i in keyArr:
            keyFile.write(str(i) + "\n")

    def __createFile(self):
        """If key file does not exist, create it"""
        if(Path(self.filename).is_file()):
            print("Keyfile exists")
        else:
            keyArr = list(range(0,self.countBase**self.keyLen))
            self.__updateFile(keyArr)
            print("Creating new keyfile")
    
    def __decToKey(self, num):
        """Convert decimal number to a key"""
        charNum = 0
        key = ""
        for i in range(self.keyLen):
            remKey = num % self.countBase
            num = math.floor(num/self.countBase)
            key += self.keyLetters[remKey]
        return key

    def __keyToDec(self, key):
        """Convert key to a decimal number"""
        #Turn key into char list
        keyList = list(key)
        keyValue = 0
        for i in range(len(keyList)):
            #convert chars to numbers
            num = self.keyLetters.index(keyList[i])
            #convert shifted ascii to base 26 counting
            keyValue += num*(self.countBase**i)
        return keyValue

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
