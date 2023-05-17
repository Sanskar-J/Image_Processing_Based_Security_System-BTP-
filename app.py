#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response
import threading

# import camera driver
# if os.environ.get('CAMERA'):
    # Camera = import_module('camera_' + os.environ['CAMERA']).Camera
# print(os.environ['CAMERA'])
# Camera = import_module('camera_opencv').Camera
# Camera2 = import_module('camera_opencv2').Camera2
# Camera2=import_module('camera_opencv').Camera
# Camera2.set_video_source(0)

#     print(Camera)
# else:
#     from camera import Camera

# Raspberry Pi camera module (requires picamera package)
#from camera_pi import Camera

app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def import_module_thread(module_name):
    """Function to import module in a separate thread."""
    return import_module(module_name)

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/video_feed2')
def video_feed2():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera2()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    thread1 = threading.Thread(target=import_module_thread, args=("camera_opencv",))
    thread2 = threading.Thread(target=import_module_thread, args=("camera_opencv2",))

    # Start the threads
    thread1.start()
    thread2.start()

    # Wait for the threads to complete
    thread1.join()
    thread2.join()

    # Get the imported camera modules
    Camera = import_module('camera_opencv').Camera
    Camera2 = import_module('camera_opencv2').Camera2

    Camera.set_video_source(0)
    x=r'C:\Users\Sanskar\Desktop\hmara btp\test.mp4'
    Camera2.set_video_source(x)
    app.run(host='0.0.0.0', threaded=True)
