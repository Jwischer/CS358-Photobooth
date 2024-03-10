#Standard packages
from os import _exit
import signal
#Installed packages
from pyautogui import size as screenSize
import gpiozero as GPIO
#Local packages
from FrontendPackage import VideoPlayer, GPIOControl, KeyGenerator

#GPIO Pins
BUTTON1 = 17
BUTTON2 = 27
LED = 22

#GPIO Interrupt Functions
def GPIO17Call(channel):
    global showCamera
    global takePhoto
    global showQR
    print("BUTTON1 Trig")
    #If in camera stage, take picture
    if(showCamera):
        takePhoto = True
    #If QR code is showing, reset to start
    elif(showQR):
        showCamera = False
        showQR = False
    #Otherwise we are on the start screen; show camera
    else:
        showCamera = True

#STILL NEED TO TEST THIS BUTTON!!!
def GPIO27Call(channel):
    global showCamera
    global showQR
    print("BUTTON2 Trig")
    #If camera showing, quit taking pictures early
    if(showCamera):
        showCamera = False
        showQR = True
    #If QR code is showing, reset to start
    elif(showQR):
        showQR = False

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
vidW, vidH = screenSize()
videoPlayer = VideoPlayer("Video", 20, [vidW, vidH])
#Inititalize key generator
keyGen = KeyGenerator("keyList.txt")

#Flags
#States: start screen -> camera -> pictures -> qr screen -> reset
showCamera = False
takePhoto = False
quitPhotos = False
showQR = False
resetBooth = False

while True:
    #Initialize
    #Generate new key
    keyGen.getNextKey()
    numPhotos = 0
    photoNameList = list("photo1")
    showCamera = True
    #Show start screen
    #Show camera
    while(showCamera):
        videoPlayer.renderFrame()
        #When time to take photo
        if(takePhoto):
            #Begin countdown
            videoPlayer.startCountdown(3, 0)
            #Take photo
            videoPlayer.renderFrame()
            videoPlayer.saveFrame(keyGen.key, "".join(photoNameList) + ".png")
            #Clear flag and flash light
            takePhoto = False
            gpioControl.flashPin(gpioControl.led, 1)
            #Update number of photos in current session
            numPhotos+=1
            #Update photo name
            photoNameList[-1] = str(int(photoNameList[-1]) + 1)
            #5 is max number of photos
            if(numPhotos == 5):
                showCamera = False
                showQR = True
            else:
                #ADD THIS SOON!!!
                #ask if user wants to continue
                pass
    while(showQR):
        #Show qr code until button press
        videoPlayer.showQRScreen(keyGen.key)
