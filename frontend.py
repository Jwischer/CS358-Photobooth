from FrontendPackage import VideoPlayer, GPIOControl, KeyGenerator
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

#NOTE: special exceptions in caller/watchdog script later
#def handler(num, frame):
#    videoPlayer.stopPlayer()
#    GPIO.cleanup()
#    _exit(0)

#Initialize GPIO
#Buttons are wired between 3.3v and target pin
gpioControl = GPIOControl([BUTTON1, BUTTON2], LED)
#GPIO events
gpioControl.addEvent(BUTTON1, GPIO17Call)
gpioControl.addEvent(BUTTON2, GPIO27Call)
#Init flags
takePhoto = False
#Initialize video player
videoPlayer = VideoPlayer()
#Inititalize key generator
try:
    keyGen = KeyGenerator(sys.argv[0])
except:
    keyGen = KeyGenerator("AAAA")

while True:
    success = videoPlayer.renderFrame()
    if(not success):
        continue
    if(takePhoto):
        videoPlayer.saveFrame(keyGen.key, "image.png")
        takePhoto = False
        gpioControl.flashPin(LED, 1)
