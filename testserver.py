import io
import picamera
import logging
import socketserver
from threading import Condition
import threading
from http import server
import cv2
import numpy as np

PAGE="""\
<html>
<head>
<title>picamera streaming</title>
</head>
<body>
<h1>PiCamera Streaming</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def findMotion(camera: picamera.PiCamera):
    try:
        print("Getting image")
        frame = np.empty((640 * 480 * 3,), dtype=np.uint8)
        camera.capture(frame, 'bgr', use_video_port=True)
        frame = frame.reshape((640, 480, 3))
        print("got image")
        oldframe = frame.copy()
        while True:
            #print("Getting image")
            frame = np.empty((640 * 480 * 3,), dtype=np.uint8)
            camera.capture(frame, 'bgr', use_video_port=True)
            frame = frame.reshape((640, 480, 3))
            #print("got image")
            diff = cv2.absdiff(frame, oldframe)
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

            # apply some blur to smoothen the frame
            diff_blur = cv2.GaussianBlur(diff_gray, (5, 5), 0)
            # to get the binary image
            _, thresh_bin = cv2.threshold(diff_blur, 20, 255, cv2.THRESH_BINARY)
            contours, hierarchy = cv2.findContours(thresh_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            #print("drawing contours")
            newframe = frame.copy()
            # to draw the bounding box when the motion is detected
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if cv2.contourArea(contour) > 300:
                    cv2.rectangle(newframe, (x, y), (x+w, y+h), (0, 255, 0), 2)
            #print("writing image")
            cv2.imwrite('testimg.jpg', frame)
            #print("Wrote Image")

            oldframe = frame.copy()
    except Exception as e:
        logging.warning(
            'Something Happend! %s',
            str(e)
        )



with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        threading.Thread(target=server.serve_forever(), daemon=True).start()
        #threading.Thread(target=findMotion(camera), daemon=True).start()
        #findMotion(camera)
        #server.serve_forever()
    finally:
        camera.stop_recording()

