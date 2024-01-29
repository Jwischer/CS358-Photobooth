import os
from time import sleep #used for delays for mouse inputs
import pyautogui
import keyboard
import cv2
import subprocess

#Photo size in pixels
PHOTO_WINDOW_SIZE_X = 600
PHOTO_WINDOW_SIZE_Y = 400

#Start hotkey functions
def aPress(): #Move mouse
    pyautogui.move(50, 50, 1, pyautogui.easeInQuad)
    sleep(0.2)
    pyautogui.click()
    sleep(0.2)
    pyautogui.scroll(2)
    
def rPress(): #Open file
    subprocess.call(["xdg-open",os.path.join(mainFolder,"README.md")]) #open readme
    
def pPress(): #Take picture
    cam = cv2.VideoCapture(0) #Grab camera
    noError,frame = cam.read() #Read from camera
    if(noError): #If successful
        #Open window and change settings
        cv2.namedWindow('Photo',cv2.WINDOW_GUI_NORMAL)
        x,y,windowWidth,Windowheight = cv2.getWindowImageRect("Photo")
        cv2.resizeWindow("Photo",PHOTO_WINDOW_SIZE_X,PHOTO_WINDOW_SIZE_Y)
        cv2.moveWindow("Photo",int((screenWidth-windowWidth)/2),int((screenHeight-Windowheight)/2))
        cv2.imshow("Photo",frame) #Show image
        cv2.waitKey(1)
        cv2.imwrite("picture.png", frame) #Save image
        cam.release()
    else:
        print("Camera Error")
        
def qPress(): #Close picture window
    try:
        cv2.destroyWindow("Photo")
    except:
        print("No window to close")
    
def escPress(): #Exit script
    os._exit(0)
#End hotkey functions

#Setup
mainFolder = os.path.dirname(__file__)
screenWidth, screenHeight = pyautogui.size() #get monitor resolution
#Hotkey definitions
keyboard.add_hotkey('a', lambda: aPress())
keyboard.add_hotkey('r', lambda: rPress())
keyboard.add_hotkey('p', lambda: pPress())
keyboard.add_hotkey('q', lambda: qPress())
keyboard.add_hotkey('esc', lambda: escPress())

while True: #Infinite loop so script wont close, hotkeys handled in thread
    pass
