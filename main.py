from os import _exit
from time import sleep #Delays
from pyautogui import size as screenSize
from signal import signal, SIGINT
from pyautogui import size as screenSize
import pygame
import cv2
import RPi.GPIO as GPIO
import numpy as np

#GPIO Pins
BUTTON1 = 17
BUTTON2 = 27
LED = 22

#Camera Settings
#W, H = int(1920), int(1080)
W, H = int(1920), int(1080)

#GPIO Interrupt Functions
def GPIO17Call(channel):
    print("BUTTON1 Trig")
    global takePhoto
    takePhoto = True

def GPIO27Call(channel):
    print("BUTTON2 Trig")

#Ctrl-C Handler
def handler(num, frame):
    capture.release()
    pygame.quit()
    GPIO.cleanup()
    _exit(0)

#Change ctrl-c to new function
signal(SIGINT, handler)
#Setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
screenWidth, screenHeight = screenSize() #get monitor resolution
#GPIO definitions
#Buttons are wired between 3.3v and
GPIO.setup([BUTTON1,BUTTON2], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, GPIO.LOW)
#GPIO events
GPIO.add_event_detect(BUTTON1, GPIO.RISING, callback=GPIO17Call, bouncetime=200)
GPIO.add_event_detect(BUTTON2, GPIO.RISING, callback=GPIO27Call, bouncetime=200)
#Init flags
takePic = False
exitWindow = False
playVideo = False
takePhoto = False

#Start capture and set capture settings
vidW, vidH = screenSize()
capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, vidW)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, vidH)
cv2.namedWindow("Video", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Video",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
capture.set(cv2.CAP_PROP_FPS, 30)

while True:
    success, framecv = capture.read()
    cv2.imshow("Video", framecv)
    cv2.waitKey(1)
    if(takePhoto):
        cv2.imwrite("image.png", framecv)
        takePhoto = False
        GPIO.output(LED, GPIO.HIGH)
        sleep(2)
        GPIO.output(LED, GPIO.LOW)
