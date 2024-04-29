#Standard packages
from os import _exit
import signal
import time
#Installed packages
import gpiozero as GPIO
#Local packages
from FrontendPackage import VideoPlayer, GPIOControl, KeyGenerator

#GPIO Pins
BUTTON1 = 17
BUTTON2 = 27
LED = 22

#QR Code Link
#Should be the link to the google form
QR_LINK = "https://forms.gle/KCeESYVUCj4moxPi7"

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

#STILL NEED TO TEST THIS BUTTON!!!
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
#vidW, vidH = screenSize()
#720p video; 1080p photos
videoPlayer = VideoPlayer("Video", [1280,720], [1920, 1080])
#Inititalize key generator
keyGen = KeyGenerator("keyList.txt")

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
        #Generate new key
        keyGen.getNextKey()
        numPhotos = 0
        #Initalize photo names
        photoNameList = list("photo1")
        #Set init instruct so user gets instructions
        initInstruct = True
        #Clear any overlays
        videoPlayer.showOverlay(None)
        #Show start screen
        videoPlayer.showStartMenu()
        while(newSession):
            pass
        
    #On first time entering photo mode
    if(showCamera and initInstruct):
        #Clear any overlays
        videoPlayer.showOverlay(None)
        #Instruct the user on what each button does
        videoPlayer.showContinueScreen()
        initInstruct = False
        
    #When time to take photo
    if(takePhoto and showCamera):
        #Clear any overlays
        videoPlayer.showOverlay(None)
        #Begin countdown
        videoPlayer.startCountdown()
        #Take photo
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
            showQR = True
            showCamera = False
        else:
            #ask if user wants to continue
            videoPlayer.showContinueScreen()
                
                
    #If end of session
    if(showQR):
        #Clear any overlays
        videoPlayer.showOverlay(None)
        #Show qr code until button press
        videoPlayer.showQRScreen(keyGen.key, QR_LINK)
        while(showQR):
            pass
