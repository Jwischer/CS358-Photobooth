#Standard libraries
import time
import subprocess
import threading
import math
import shutil
from pathlib import Path
import os
#Raspberry Pi libraries
from gpiozero import LED, Button
#Installed libraries
import cv2
import numpy
import qrcode
from picamera2 import Picamera2, Preview
from PIL import Image

class VideoPlayer:
    def __init__(self, playerName, vidRes, camRes):
        self.playerName = playerName
        self.capture = cv2.VideoCapture(0)
        self._path = Path("Images/")
        self.vidWIDTH, self.vidHEIGHT = vidRes
        self.camWIDTH, self.camHEIGHT = camRes
        self.picam2 = Picamera2()
        #Initialize qr code settings
        self.qr = qrcode.QRCode(
            version = None,
            error_correction = qrcode.constants.ERROR_CORRECT_L,
            box_size = 10,
            border = 4,
        )
        #Set camera config
        self.videoConfig = self.picam2.create_preview_configuration(main={"size": (self.vidWIDTH, self.vidHEIGHT)}, display="main", buffer_count = 3)
        #Set up image capture configuration
        self.photoConfig = self.picam2.create_still_configuration(main={"size": (self.camWIDTH, self.camHEIGHT)})
        subprocess.call("mkdir -m 777 Images", shell=True, stderr=subprocess.DEVNULL)
        #Start video and set video config
        self.picam2.start_preview(Preview.DRM, x=1, y=1, width=self.vidWIDTH, height=self.vidHEIGHT)
        #auto-optimize irregular resolutions
        self.picam2.align_configuration(self.videoConfig)
        #Start picam in video mode
        self.picam2.configure(self.videoConfig)
        self.picam2.start()
    
    def stopPlayer(self):
        self.picam2.stop_preview()
        self.picam2.stop()

    def saveFrame(self, folderKey, imageName):
        print(folderKey + " " + imageName)
        #Create folder if it does not exist
        subprocess.call("sudo mkdir -m 777 Images/" + folderKey, shell=True, stderr=subprocess.DEVNULL)
        #capture image
        self.picam2.switch_mode_and_capture_file(self.photoConfig, str(self._path / folderKey / imageName))
        #switch back to video
        self.picam2.switch_mode(self.videoConfig)
        
    def startCountdown(self):
        """Countdown from 3 to 1 inclusive, number printed in center of window"""
        #Display 3 overlay
        self.showOverlay("3overlay")
        #Wait for 1 second
        time.sleep(1)
        #continue counting...
        self.showOverlay("2overlay")
        time.sleep(1)
        self.showOverlay("1overlay")
        time.sleep(1)
        #self.showOverlay("0overlay")
        #time.sleep(1)
        #Clear overlay
        self.showOverlay(None)
    
    def showStartMenu(self):
        self.showOverlay("startupscreenfilled")
        
    def showContinueScreen(self):
        self.showOverlay("takeendoverlay")
        
    def showQRScreen(self, key, qrLink):
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = "Key: " + key
        scale = 4
        thickness = 3
        spacing = 50
        #Load overlay image
        overlay = cv2.imread("Overlays/QRCodeOverlay.png", cv2.IMREAD_UNCHANGED)
        #Add key text to overlay image
        textSize = cv2.getTextSize(text, font, scale, thickness)[0]
        coords = [int((1920-textSize[0])/2), int((1080-textSize[1])/2)+spacing]
        #Note OpenCV uses BGRA rather than RGBA
        cv2.putText(overlay, text, coords, font, scale, (0,48,92,255), thickness+4, cv2.LINE_AA)
        cv2.putText(overlay, text, coords, font, scale, (10,184,245,255), thickness, cv2.LINE_AA)
        #Set qr code data
        self.qr.add_data(qrLink)
        #Generate qr code (BGR color values)
        qrCode = self.qr.make_image(fill_color = (0, 48, 92), back_color = (214 , 217, 218))
        #Convert to numpy array using RGBA
        qrCode = numpy.array(qrCode.convert("RGBA"))
        #Bottom half of overlay can be used for qr code
        qrDim = qrCode.shape
        overlayDim = overlay.shape
        #Calculate qr code start coordinates
        startCoord = [overlayDim[0]/2 - qrDim[0]/2 + overlayDim[0]/4, overlayDim[1]/2 - qrDim[1]/2]
        #Calculate qr code end coordinates
        endCoord = [startCoord[0] + qrDim[0], startCoord[1] + qrDim[1]]
        #Replace pixels with qr code
        overlay[int(startCoord[0]):int(endCoord[0]), int(startCoord[1]):int(endCoord[1]), :] = qrCode
        #Show overlay
        self.showOverlay(overlay)
        
    def showOverlay(self, overlay):
        #If None; clear overlay
        if overlay is None:
            self.picam2.set_overlay(overlay)
            return
        try:
            #If string; display corresponding overlay
            overlayImg = cv2.imread("Overlays/" + overlay + ".png", cv2.IMREAD_UNCHANGED)
            self.picam2.set_overlay(cv2.cvtColor(overlayImg, cv2.COLOR_BGRA2RGBA))
        except:
            #If image; display image
            self.picam2.set_overlay(cv2.cvtColor(overlay, cv2.COLOR_BGRA2RGBA))
        

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
            keyArr = list(range(0,26**self.keyLen))
            self.__updateFile(keyArr)
            print("Creating new keyfile")
    
    def __decToKey(self, num):
        charNum = 0
        key = ""
        for i in range(self.keyLen):
            remKey = num % 26
            num = math.floor(num/26)
            key += chr(remKey + self.asciiBase)
        return key

    def __keyToDec(self, key):
        #Turn key into char list
        keyList = list(key)
        keyValue = 0
        for i in range(len(keyList)):
            #convert chars to ascii; shift so that A = 1, B = 2, etc
            num = ord(keyList[i]) - self.asciiBase
            #convert shifted ascii to base 26 counting
            keyValue += num*(26**i)
        return keyValue
            
        
class StorageManager():

    def __init__(self, managerPath):
        self.path = managerPath
        
    def CheckStorageNoPrint(self, maxItems):
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
            shutil.rmtree(oldItem)
            return True
        return False
        
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
            shutil.rmtree(oldItem)
            return True, str(oldItem).split("/")[-1]
        return False, None

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
