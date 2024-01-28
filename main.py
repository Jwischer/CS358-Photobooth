import os
from time import sleep #used for delays for mouse inputs
from pyautogui import size as screenSize #used to get monitor resolution
from pynput.mouse import Controller, Button #used to control mouse input
from pynput.keyboard import Listener, Key #used to control keyboard
import cv2

#Photo size in pixels
PHOTO_WINDOW_SIZE_X = 600
PHOTO_WINDOW_SIZE_Y = 400

#Hotkey function
def on_press(key):
    try: #standard alphanumeric keys go here
        if(key.char == 'a'): #Move mouse
            mouse.position = (screenWidth/2,screenHeight/2)
            sleep(0.2)
            mouse.click(Button.left)
            sleep(0.2)
            mouse.scroll(0, 5)
        if(key.char == 'r'): #Open file
            os.startfile(os.path.join(mainFolder,"README.md")) #open readme
        if(key.char == 'p'): #Take picture
            cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            noError,frame = cam.read()
            if(noError):
                cv2.namedWindow("Photo", cv2.WINDOW_NORMAL)
                x,y,windowWidth,Windowheight = cv2.getWindowImageRect("Photo")
                cv2.resizeWindow("Photo",PHOTO_WINDOW_SIZE_X,PHOTO_WINDOW_SIZE_Y)
                cv2.moveWindow("Photo",int((screenWidth-windowWidth)/2),int((screenHeight-Windowheight)/2))
                cv2.imshow("Photo",frame)
                cv2.waitKey(1)
                cv2.imwrite("picture.png", frame)
                cam.release()
            else:
                print("Camera Error")
        if(key.char == 'q'): #Close picture window
            cv2.destroyWindow("Photo")
    except: #special keys go here
        if(key == Key.esc):
            os._exit(0)

#Setup
mainFolder = os.path.dirname(__file__)
screenWidth, screenHeight = screenSize() #get monitor resolution
mouse = Controller()
keyboard = Listener(on_press=on_press)
keyboard.start() #begin listening for keystrokes, threaded

while True: #Infinite loop so script wont close, hotkeys handled in thread
    pass