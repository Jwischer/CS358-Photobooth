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
import qrcode

class VideoPlayer:
    def __init__(self, playerName, fps, resolution):
        self.currCdVal = 0
        self.fps = fps
        self.playerName = playerName
        self.resolution = resolution
        self.capture = cv2.VideoCapture(0)
        self._path = Path("Images/")
        self.success = False
        subprocess.call("mkdir -m 777 Images", shell=True, stderr=subprocess.DEVNULL)
        self.currFrame = None
        #Initialize frame grabbing thread
        self.frameThread = threading.Thread(target=self.__updateFrame, args=[], daemon=True)
        #Start capture and set capture settings
        vidW, vidH = screenSize()
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.capture.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)
        self.capture.set(cv2.CAP_PROP_FPS, self.fps)
        cv2.namedWindow(self.playerName, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(self.playerName,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        #Start thread
        self.frameThread.start()
    
    def stopPlayer(self):
        self.capture.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)

    def __updateFrame(self):
        """Function for use in the frame grabber thread, continuously grabs new frames"""
        while True:
            if self.capture.isOpened():
                self.success, self.currFrame = self.capture.read()
                time.sleep(1/self.fps)

    def renderFrame(self):
        try:
            #vidFrame = cv2.resize(self.currFrame, (int(self.resolution[0]), int(self.resolution[1])))
            cv2.imshow("Video", self.currFrame)
            cv2.waitKey(20)
        except:
            pass
        return self.success

    def saveFrame(self, folderKey, imageName):
        print(folderKey + " " + imageName)
        #Create folder if it does not exist
        subprocess.call("sudo mkdir -m 777 Images/" + folderKey, shell=True, stderr=subprocess.DEVNULL)
        #Write image to folder
        cv2.imwrite(str(self._path / folderKey / imageName), self.currFrame)
        
    def startCountdown(self, start, end):
        """Countdown from start to end inclusive, number printed in center of window"""
        self.currCdVal = start
        #Create countdown thread
        countThread = threading.Thread(target=self.__countdownVal, args=[start, end], daemon=True)
        countThread.start()
        while True:
            #Copy original image into new mat
            textImg = cv2.copyTo(self.currFrame, numpy.ones(self.currFrame.shape, "uint8"))
            #Place current number in the center
            putTextCenter(textImg, str(self.currCdVal), cv2.FONT_HERSHEY_SIMPLEX, 5, (255,255,255), 10)
            #Show image and wait for a second
            if(self.currCdVal == end-1):
                break
            cv2.imshow(self.playerName, textImg)
            cv2.waitKey(1)
            
    def __countdownVal(self, start, end):
        for i in range(start, end-2, -1):
            self.currCdVal = i
            time.sleep(1)
    
    def showStartMenu(self):
        pass
        
    def showContinueScreen(self):
        pass
        
    def showQRScreen(self, key):
        textRatio = 0.25
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = ["Key: " + key, "Scan the QR code and fill out the form for your pictures!"]
        scale = [4,2,2,2]
        thickness = [3,2,2,2]
        spacing=10
        basePosShift=50
        #Create a QR code
        pilQrCode = qrcode.make(text).convert('RGB')
        #Convert into cv2 image
        qrImg = cv2.cvtColor(numpy.array(pilQrCode), cv2.COLOR_RGB2BGR)
        #Place QR code in center of bottom image
        height, width, channels = qrImg.shape
        lrBorder = (self.resolution[0]-width)/2 #Border on left and right of QR code
        tbBorder = ((self.resolution[1]*(1-textRatio))-height)/2 #Border on top and bottom of QR code
        #Get start and end coordinates for QR code
        startCoords = [int(tbBorder), int(lrBorder)]
        endCoords = [startCoords[0]+height, startCoords[1]+width]
        qrCenterImg = numpy.zeros((int(self.resolution[1]*(1-textRatio)),self.resolution[0],3), numpy.uint8)
        qrCenterImg[startCoords[0]:endCoords[0],startCoords[1]:endCoords[1],:] = qrImg
        textsize = []
        for i in range(len(text)):
            #Calculate size of text
            textsize.append(cv2.getTextSize(text[i], font, scale[i], thickness[i]))
        #basePos = highest text can go without going off screen + shift
        basePos = textsize[0][0][1]+basePosShift
        textCenter = [int(self.resolution[0]/2), int((self.resolution[1]*textRatio)/2)]
        #Create text image
        textImg = numpy.zeros((int(self.resolution[1]*textRatio),self.resolution[0],3), numpy.uint8)
        textImg = cv2.putText(textImg, text[0], (textCenter[0]-int(textsize[0][0][0]/2),basePos), font, scale[0], (255,255,255), thickness[0], cv2.LINE_AA)
        currPos = textsize[0][0][1]+spacing
        for i in range(1,len(text)):
            textImg = cv2.putText(textImg, text[i], (textCenter[0]-int(textsize[i][0][0]/2),basePos+currPos), font, scale[i], (255,255,255), thickness[i], cv2.LINE_AA)
            currPos+=textsize[i][0][1]+spacing
        images = [textImg, qrCenterImg]
        #Combine images and display
        combImg = cv2.vconcat(images)
        cv2.imshow(self.playerName, combImg)
        cv2.waitKey(1)

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
        
    def close(self):
        self.btn1.close()
        self.btn2.close()
        self.led.close()

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
        """If key file does not exist, create it"""
        if(Path(self.filename).is_file()):
            print("Keyfile exists")
        else:
            keyArr = list(range(0,26**self.keyLen))
            self.__updateFile(keyArr)
            print("Creating new keyfile")
    
    def __decToKey(self, num):
        """ """
        charNum = 0
        key = ""
        for i in range(self.keyLen):
            remKey = num % 26
            num = math.floor(num/26)
            key += chr(remKey+self.asciiBase)
        return key
        
def putTextCenter(image, text, font, scale, color, thickness, linetype=cv2.LINE_AA):
    """Places text in the middle of the image"""
    textSize = cv2.getTextSize(text, font, scale, thickness)
    posX = int((image.shape[1] - textSize[0][0]) / 2)
    posY = int((image.shape[0] + (textSize[0][1] - textSize[1])) / 2)
    cv2.putText(image, text, (posX, posY), font, scale, color, thickness, cv2.LINE_AA)

def putTextBottom(image, text, font, scale, color, thickness, linetype=cv2.LINE_AA):
    """Places text in the bottom of the image"""
    textSize = cv2.getTextSize(text, font, scale, thickness)
    posX = int((image.shape[1] - textSize[0][0]) / 2)
    posY = int((image.shape[0]) - (textSize[0][1] - textSize[1]) / 2)
    cv2.putText(image, text, (posX, posY), font, scale, color, thickness, cv2.LINE_AA)

def putTextBottomLeft(image, text, font, scale, color, thickness, linetype=cv2.LINE_AA):
    """Places text in the bottom left of the image"""
    textSize = cv2.getTextSize(text, font, scale, thickness)
    posX = int((image.shape[1] / 2 - textSize[0][0]) / 2)
    posY = int((image.shape[0]) - (textSize[0][1] - textSize[1]) / 2)
    cv2.putText(image, text, (posX, posY), font, scale, color, thickness, cv2.LINE_AA)

def putTextBottomRight(image, text, font, scale, color, thickness, linetype=cv2.LINE_AA):
    """Places text in the bottom right of the image"""
    textSize = cv2.getTextSize(text, font, scale, thickness)
    posX = int(image.shape[1] - textSize[0][0] - (image.shape[1] / 2 - textSize[0][0]) / 2)
    posY = int((image.shape[0]) - (textSize[0][1] - textSize[1]) / 2)
    cv2.putText(image, text, (posX, posY), font, scale, color, thickness, cv2.LINE_AA)
