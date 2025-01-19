# Quick test to see if the camera works
from time import sleep
from picamera import PiCamera

camera = PiCamera()
camera.resolution = (1024,768)
# Uncomment if display exists
camera.start_preview()
sleep(2)
camera.capture('test.jpg')