#frontend.py  Copyright (C) 2024  Valparaiso University

#Standard packages
from os import _exit
import signal
import time
import pathlib
import configparser
#Installed packages
import gpiozero as GPIO
#Local packages
from FrontendPackage import VideoPlayer, GPIOControl, KeyGenerator, StorageManager

#Parse config.ini
config = configparser.ConfigParser()
config.read("config.ini")

#GPIO Pins
BUTTON1 = 17
BUTTON2 = 27
LED = 22

#Parse picamera configs into arrays
#Resolution of viewport
vidSize = config['PICAMERA']['VideoViewportSize'].split(',')
for i in range(len(vidSize)):
    vidSize[i] = vidSize[i].strip()
    #Convert string to int
    vidSize[i] = int(vidSize[i])

#Resolution of video
vidResolution = config['PICAMERA']['VideoResolution'].split(',')
for i in range(len(vidResolution)):
    vidResolution[i] = vidResolution[i].strip()
    vidResolution[i] = int(vidResolution[i])

#Resolution of pictures
camResolution = config['PICAMERA']['CameraResolution'].split(',')
for i in range(len(camResolution)):
    camResolution[i] = camResolution[i].strip()
    camResolution[i] = int(camResolution[i])

#Path to images folder
imagePath = pathlib.Path("Images/")

#QR Code Link
#Should be the link to the google form
QR_LINK = config['URLS']['FormUrl']
#QR screen timeout in ms
qrTimeout = int(config['TIMEOUT']['QrTimeout'])

#GPIO Interrupt Functions
def GPIO17Call(channel):
    global newSession
    global showCamera
    global takePhoto
    global showQR
    print("BUTTON1 Trig")
    #Cycle through states on press
    #If on the start screen
    if(newSession):
        #Advance to camera
        newSession = False
        showCamera = True
    #If in camera
    elif(showCamera):
        #Take a photo
        takePhoto = True
    #If QR code is showing
    elif(showQR):
        #Reset to start
        showQR = False
        newSession = True

def GPIO27Call(channel):
    global newSession
    global contScreen
    global showCamera
    global showQR
    print("BUTTON2 Trig")
    #If on the start screen
    if(newSession):
        #Advance to camera
        newSession = False
        showCamera = True
    #If camera is showing
    elif(showCamera):
        #Advance to QR code early
        showCamera = False
        showQR = True
    #If QR code is showing, reset to start
    elif(showQR):
        showQR = False
        newSession = True

#Special ctrl+c handler function
def handler(num, frame):
    videoPlayer.stopPlayer()
    gpioControl.close()
    _exit(0)

#Set up ctrl+c exception handler
signal.signal(signal.SIGINT, handler)

#Initialize GPIO
#Buttons are wired between 3.3v and target pin
gpioControl = GPIOControl([BUTTON1, BUTTON2], LED)
#GPIO events
gpioControl.addEvent(gpioControl.btn1, GPIO17Call)
gpioControl.addEvent(gpioControl.btn2, GPIO27Call)
#Initialize video player
videoPlayer = VideoPlayer("Video", vidResolution, camResolution, vidSize)
#Inititalize key generator
keyGen = KeyGenerator("keyList.txt")
#Initialize storage manager
fileManager = StorageManager(imagePath)

#Flags
#States: start screen -> camera -> pictures -> qr screen -> reset
newSession = True
showCamera = False
takePhoto = False
showQR = False
initInstruct = True

while True:
    if(newSession):
        #Initialize
        #If too many files; delete oldest
        status, fileKey = fileManager.CheckStorage(500)
        #If a file was deleted add its key back into keyGen
        if(status):
             #Add key back to useable keys
             keyGen.addKey(fileKey)
        #Generate new key
        keyGen.getNextKey()
        numPhotos = 0
        #Initalize photo names
        photoNameList = list("photo1")
        #Set init instruct so user gets instructions
        initInstruct = True
        #Show start screen
        videoPlayer.showStartMenu()
        while(newSession):
            pass

    #On first time entering photo mode
    if(showCamera and initInstruct):
        #Instruct the user on what each button does
        videoPlayer.showContinueScreen()
        initInstruct = False

    #When time to take photo
    if(takePhoto and showCamera):
        #Disable GPIO
        gpioControl.addEvent(gpioControl.btn1, None)
        gpioControl.addEvent(gpioControl.btn2, None)
        #Begin countdown
        videoPlayer.startCountdown()
        #Take photo
        videoPlayer.saveFrame(keyGen.key, "".join(photoNameList) + ".jpg")
        #Clear flag and flash light
        takePhoto = False
        gpioControl.flashPin(gpioControl.led, 1)
        #Update number of photos in current session
        numPhotos+=1
        #Update photo name
        photoNameList[-1] = str(int(photoNameList[-1]) + 1)
        #5 is max number of photos
        if(numPhotos == 5):
            showQR = True
            showCamera = False
        else:
            #ask if user wants to continue
            videoPlayer.showContinueScreen()
        #Enable GPIO
        gpioControl.addEvent(gpioControl.btn1, GPIO17Call)
        gpioControl.addEvent(gpioControl.btn2, GPIO27Call)

    #If end of session
    if(showQR):
        #Show qr code until button press
        videoPlayer.showQRScreen(keyGen.key, QR_LINK)
        #Wait for qrTimeout ms or until button pressed
        for i in range(qrTimeout):
            time.sleep(0.001)
            if(not showQR):
                break
        showQR = False
        newSession = True
