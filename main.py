#!/usr/bin/env python

import io
import time
import picamera
import numpy as np
from PIL import Image, ImageDraw

FILE_PATTERN        = 'motion%02d.h264'     # the file pattern in which to record videos
FILE_BUFFER         = 1048576               # the size of the file buffer (bytes)

REC_RESOLUTION      = (1280, 720)           # the recording resolution
REC_FRAMERATE       = 24                    # the recording framerate
REC_SECONDS         = 10                    # number of seconds to store in ring buffer
REC_BITRATE         = 1000000               # bitrate for H.264 encoder

MOTION_MAGNITUDE    = 60                    # the magnitude of vectors required for motion
MOTION_VECTORS      = 10                    # the number of vectors required to detect motion



def main():
    with picamera.PiCamera() as camera:
        camera.resolution = REC_RESOLUTION
        camera.framerate = REC_FRAMERATE
        time.sleep(2)

        camera.start_preview()
        
        ring_buffer = picamera.PiCameraCircularIO(
            camera, seconds=REC_SECONDS, bitrate=REC_BITRATE
        )

        file_number = 1
        file_output = io.open(
            FILE_PATTERN % file_number, 'wb', buffering=FILE_BUFFER
        )

        camera.start_recording(
            ring_buffer, format='h264', bitrate=REC_BITRATE,
            intra_period=REC_FRAMERATE
        )

if __name__ == '__main__':
    main()