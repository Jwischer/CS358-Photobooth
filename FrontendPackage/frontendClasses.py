#Standard libraries
import time
import subprocess
import threading
import math
#Raspberry Pi libraries
from gpiozero import LED, Button
#Installed libraries
import cv2
from pathlib import Path
from pyautogui import size as screenSize
import numpy

class VideoPlayer:
    def __init__(self, playerName, fps, resolution):
        self.playerName = playerName
        self.resolution = resolution
        self.capture = cv2.VideoCapture(0)
        self._path = Path("Images/")
        self.success = False
        subprocess.call("mkdir -m 777 Images", shell=True, stderr=subprocess.DEVNULL)
        self.currFrame = None
        #Initialize frame grabbing thread
        self.frameThread = threading.Thread(target=self.__updateFrame, args=(), daemon=True)
        #Start capture and set capture settings
        vidW, vidH = screenSize()
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.capture.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
        self.capture.set(cv2.CAP_PROP_FPS, fps)
        cv2.namedWindow(self.playerName, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(self.playerName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        #Start thread
        self.frameThread.start()
    
    def stopPlayer(self):
        self.capture.release()

    def __updateFrame(self):
        """Function for use in the frame grabber thread, continuously grabs new frames"""
        while True:
            if self.capture.isOpened():
                self.success, self.currFrame = self.capture.read()
            time.sleep(0.01)

    def renderFrame(self):
        try:
            #vidFrame = cv2.resize(self.currFrame, (int(self.resolution[0]), int(self.resolution[1])))
            cv2.imshow("Video", self.currFrame)
            cv2.waitKey(1)
        except:
            pass
        return self.success

    def saveFrame(self, folderKey, imageName):
        print(folderKey + " " + imageName)
        #Create folder if it does not exist
        subprocess.call("sudo mkdir -m 777 Images/" + folderKey, shell=True, stderr=subprocess.DEVNULL)
        #Write image to folder
        cv2.imwrite(str(self._path / folderKey / imageName), self.currFrame)

class GPIOControl:
    def __init__(self, inputs, outputs):
        self.btn1 = Button(inputs[0], pull_up=False)
        self.btn2 = Button(inputs[1], pull_up=False)
        self.led = LED(outputs)
    
    def addEvent(self, targetInput, callbackFunction):
        targetInput.when_pressed = callbackFunction

    def flashPin(self, outputPin, length):
        outputPin.on()
        time.sleep(length)
        outputPin.off()

class KeyGenerator:
    def __init__(self, filename):
        #Initialize key
        self.key = None
        #Set file name
        self.filename = filename
        #Set starting key length
        self.keyLen = 4
        #Set ascii base
        self.asciiBase = ord('A')
        #Create text file containing key codes
        self.__createFile()
        
    def getNextKey(self):
        keyCode, updatedList = self.__getKeyCode()
        self.__updateFile(updatedList)
        self.key = self.__decToKey(keyCode)
        return self.key
    
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
        return int(keyCode), updatedList
            
    def __updateFile(self, keyArr):
        keyFile = open(self.filename, "w")
        keyFile.write("")
        keyFile.close()
        keyFile = open(self.filename, "a")
        for i in keyArr:
            keyFile.write(str(i) + "\n")

    def __createFile(self):
        keyArr = list(range(0,26**self.keyLen))
        self.__updateFile(keyArr)
    
    def __decToKey(self, num):
        """ """
        charNum = 0
        key = ""
        for i in range(self.keyLen):
            remKey = num % 26
            num = math.floor(num/26)
            key += chr(remKey+self.asciiBase)
        return key
    
