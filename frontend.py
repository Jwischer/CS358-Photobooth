from FrontendPackage import VideoPlayer, GPIOControl, KeyGenerator
from pyautogui import size as screenSize
import sys

#GPIO Pins
BUTTON1 = 17
BUTTON2 = 27
LED = 22

#GPIO Interrupt Functions
def GPIO17Call(channel):
    print("BUTTON1 Trig")
    global takePhoto
    takePhoto = True

def GPIO27Call(channel):
    print("BUTTON2 Trig")
    keyGen.makeNewKey()

#NOTE: special exceptions in caller/watchdog script later
#def handler(num, frame):
#    videoPlayer.stopPlayer()
#    GPIO.cleanup()
#    _exit(0)

#Initialize GPIO
#Buttons are wired between 3.3v and target pin
gpioControl = GPIOControl([BUTTON1, BUTTON2], LED)
#GPIO events
gpioControl.addEvent(gpioControl.btn1, GPIO17Call)
gpioControl.addEvent(gpioControl.btn2, GPIO27Call)
#Init flags
takePhoto = False
#Initialize video player
vidW, vidH = screenSize()
videoPlayer = VideoPlayer("Video", 30, [vidW, vidH])
#Inititalize key generator
try:
    keyGen = KeyGenerator(sys.argv[1])
except:
    keyGen = KeyGenerator("AAAA")

while True:
    success = videoPlayer.renderFrame()
    if(not success):
        continue
    if(takePhoto):
        print(keyGen.key)
        videoPlayer.saveFrame(keyGen.key, "image.png")
        takePhoto = False
        gpioControl.flashPin(gpioControl.led, 1)
