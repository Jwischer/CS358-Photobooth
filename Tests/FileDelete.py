import os
import pathlib
import shutil
import time

class StorageManager():

    def __init__(self, managerPath):
        self.path = managerPath

    def CheckStorage(self, maxItems):
        #Get number of items
        items = os.listdir(self.path)
        #If more than maxItems folders
        if(len(items) > maxItems):
            #Construct full paths
            fullPaths = []
            for i in items:
                fullPaths.append(self.path / i)
            #Delete oldest item
            oldItem = min(fullPaths, key = os.path.getctime)
            print("Deleted: " + str(oldItem))
            shutil.rmtree(oldItem)
            return True
        return False

#Path must be an empty directory for test to work
keyPath = pathlib.Path('testdir')
fileManager = StorageManager(keyPath)

numDir = 1000
maxDir = 100
#Create test directory
try:
    os.mkdir(keyPath)
except:
    shutil.rmtree(keyPath)
    os.mkdir(keyPath)
#Create numDir directories (names: Fold1, Fold2, Fold3, ...)
for i in range(1, numDir+1):
    os.mkdir(keyPath / str(i))
    time.sleep(0.01)

testVar = 0
for i in range(1, numDir+1):
    testResult = fileManager.CheckStorage(maxDir)
    if(testResult == True):
        testVar += 1
    else:
        if(numDir - testVar == maxDir):
            print("Test Success: " + str(numDir - testVar) + " directories remain; expecting " + str(maxDir))
            break
        else:
            print("Test Failed: " + str(numDir - testVar) + " directories remain; expecting " + str(maxDir))
            break

shutil.rmtree(keyPath)
