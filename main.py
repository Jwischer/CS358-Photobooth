import os
from time import sleep #used for delays for mouse inputs
from pyautogui import size as screenSize #used to get monitor resolution
from pynput.mouse import Controller, Button #used to control mouse input
from pynput.keyboard import Listener, Key #used to control keyboard

#Hotkey function
def on_press(key):
    try: #standard alphanumeric keys go here
        if(key.char == 'a'):
            mouse.position = (screenWidth/2,screenHeight/2)
            sleep(0.2)
            mouse.click(Button.left)
            sleep(0.2)
            mouse.scroll(0, 5)
        if(key.char == 'r'):
            os.startfile(os.path.join(mainFolder,"README.md")) #open readme
    except: #special keys go here
        if(key == Key.esc):
            print("esc")
            os._exit(0)

#Setup
mainFolder = os.path.dirname(__file__)
screenWidth, screenHeight = screenSize() #get monitor resolution
mouse = Controller()
keyboard = Listener(on_press=on_press)
keyboard.start() #begin listening for keystrokes, threaded

while True: #Infinite loop so script wont close, hotkeys handled in thread
    pass