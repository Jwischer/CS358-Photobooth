import os
from time import sleep #used for delays for mouse inputs
import pyautogui
import keyboard
import subprocess
import pygame.camera
import pygame.image

#Start hotkey functions
def aPress(): #Move mouse
    pyautogui.move(50, 50, 1, pyautogui.easeInQuad)
    sleep(0.2)
    pyautogui.click()
    sleep(0.2)
    pyautogui.scroll(2)
    
def rPress(): #Open file
    subprocess.call(["xdg-open",os.path.join(mainFolder,"README.md")]) #open readme
    
def vPress(): #Take video
    global playVideo
    playVideo = True

def qPress(): #Close picture window
    global exitWindow
    exitWindow = True
    
def escPress(): #Exit script
    os._exit(0)
#End hotkey functions

#Setup
mainFolder = os.path.dirname(__file__)
screenWidth, screenHeight = pyautogui.size() #get monitor resolution
#Hotkey definitions
keyboard.add_hotkey('a', lambda: aPress())
keyboard.add_hotkey('r', lambda: rPress())
keyboard.add_hotkey('v', lambda: vPress())
keyboard.add_hotkey('q', lambda: qPress())
keyboard.add_hotkey('esc', lambda: escPress())
#Init flags
takePic = False
exitWindow = False
playVideo = False

while True: #Infinite loop to check for flags
    if(playVideo):
        #Initialize camera window
        pygame.camera.init()
        cameras = pygame.camera.list_cameras()
        webcam = pygame.camera.Camera(cameras[0])
        webcam.start()
        #grab initial frame
        img = webcam.get_image()
        WIDTH = img.get_width()
        HEIGHT = img.get_height()
        screen = pygame.display.set_mode((WIDTH,HEIGHT), pygame.NOFRAME)
        while(not exitWindow):
            img = webcam.get_image()
            pygame.display.set_caption("pyGame Camera View")
            screen.blit(img, (0,0))
            pygame.display.flip()
        webcam.stop()
        playVideo = False
        
    if(exitWindow):
        pygame.quit()
        exitWindow = False
        needInit = True
