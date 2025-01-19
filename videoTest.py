import socket
import time
import picamera
from io import BytesIO
import ffmpeg

server_url = "http://0.0.0.0:8081"

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24

#server_socket = socket.socket()
#server_socket.bind(('0.0.0.0', 8081))
print("Waiting for connection...")
#server_socket.listen(0)
# Accept a single connection and make a file-like object out of it
#connection = server_socket.accept()[0].makefile('wb')
print("Connected!")
try:
    #stream = BytesIO()
    #camera.start_recording(stream, format='h264')
    try:
        while True:
            camera.capture("temp.png", format="png", use_video_port=True)
            #camera.wait_recording(0)
            #process = (
            #    ffmpeg.input('pipe:') 
            #        .output('test.mp4')
            #        .overwrite_output()
            #        .run_async(pipe_stdin=True)
            #)

            out, s = (
                ffmpeg
                .input("temp.png")
                .output(
                    server_url,
                    codec = "mp4",
                    listen = 1,
                    f="webm"
                )
            )
            #process.communicate(input=stream.getbuffer())
    finally:
        camera.stop_recording()
finally:
    connection.close()
    server_socket.close()