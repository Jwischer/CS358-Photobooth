import time
from pathlib import Path
from pyautogui import size as screenSize
import cv2
import RPi.GPIO as GPIO
import subprocess

class VideoPlayer:
    def __init__(self, playerName, fps):
        self.playerName = playerName
        self.capture = cv2.VideoCapture(0)
        self._path = Path("/Images")
        #Start capture and set capture settings
        vidW, vidH = screenSize()
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, vidW)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, vidH)
        cv2.namedWindow(self.playerName, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(self.playerName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.capture.set(cv2.CAP_PROP_FPS, fps)
    
    def stopPlayer(self):
        self.capture.release()

    def renderFrame(self):
        success, framecv = self.capture.read()
        cv2.imshow("Video", framecv)
        cv2.waitKey(1)
        return success

    def saveFrame(self, folderKey, imageName):
        #Create folder if it does not exist
        subprocess.call("mkdir Images\\" + folderKey, shell=True, stderr=subprocess.DEVNULL)
        #Write image to folder
        cv2.imwrite(self._path / folderKey / imageName, framecv)

class GPIOControl:
    def __init__(self, inputs, outputs):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(inputs, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(outputs, GPIO.OUT)
        GPIO.output(LED, GPIO.LOW)
    
    def addEvent(self, targetInput, callbackFunction):
        GPIO.add_event_detect(targetInput, GPIO.RISING, callback=callbackFunction, bouncetime=200)

    def flashPin(self, outputPin, length):
        GPIO.output(outputPin, GPIO.high)
        time.sleep(length)
        GPIO.output(outputPin, GPIO.low)

class KeyGenerator:
    def __init__(self, initKey):
        self.key = initKey
    
    def makeNewKey(self):
        keyList = list(self.key)
        #Generate new key
        newKey = __findNextKey(keyList)
        #Turn list of chars into string
        self.key = newKey
        return newKey

    def __findNextKey(self, keyList):
        """Private function, generates new key"""
        charNum = 0
        for char in keyList:
            if(char=='Z'):
                charNum += 1
                #if key is all Zs (out of keys for length)
                if(charNum == len(keyList)):
                    #Make the key one more character, set all to A
                    keyList = (charNum+1)*"A"
                continue
            #Increment character
            keyList[charNum] = chr(ord(char) + 1)
            break
        return ''.join(keyList)