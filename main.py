import os
from time import sleep #used for delays for mouse inputs
from pyautogui import size as screenSize #used to get monitor resolution
from pynput.mouse import Controller, Button #used to control mouse input
from pynput.keyboard import Listener, Key #used to control keyboard
import cv2

#Video size in pixels
VIDEO_WINDOW_SIZE_X = 600
VIDEO_WINDOW_SIZE_Y = 400

#Hotkey function
def onPress(key):
    try: #standard alphanumeric keys go here
        if(key.char == 'a'): #Move mouse
            mouse.position = (100,100)
            mouse.click(Button.left)
            sleep(0.2)
            mouse.scroll(0, 5)
        if(key.char == 'r'): #Open file
            os.startfile(os.path.join(mainFolder,"README.md")) #open readme
        if(key.char == 'v'): #Start video
            #Setup video and move to center of screen
            cv2.namedWindow("Video", cv2.WINDOW_NORMAL)
            x,y,windowWidth,Windowheight = cv2.getWindowImageRect("Video")
            cv2.resizeWindow("Video",VIDEO_WINDOW_SIZE_X,VIDEO_WINDOW_SIZE_Y)
            cv2.moveWindow("Video",int((screenWidth-windowWidth)/2),int((screenHeight-Windowheight)/2))
            #Make window active (may be a better way to do this)
            mousePos = mouse.position
            mouse.position = ((screenWidth-windowWidth)/2,(screenHeight-Windowheight)/2)
            mouse.click(Button.left)
            mouse.position = mousePos
            #Init camera
            cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            #Loop rendering frames
            while(True):
                noError,frame = cam.read()
                if(noError):
                    cv2.imshow("Video",frame)
                    #Close window when 'w' pressed
                    if(cv2.waitKey(1) & 0xFF == ord('w')):
                        cam.release()
                        cv2.destroyWindow("Video")
                        break
                else:
                    print("Camera Error")
    except: #special keys go here
        if(key == Key.esc):
            os._exit(0)

#Setup
screenWidth, screenHeight = screenSize()
mainFolder = os.path.dirname(__file__)
mouse = Controller()
keyboard = Listener(on_press=onPress)
keyboard.start() #begin listening for keystrokes, threaded

while True: #Infinite loop so script wont close, hotkeys handled in thread
    pass