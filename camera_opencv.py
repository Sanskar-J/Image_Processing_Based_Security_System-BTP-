import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2
import numpy as np
import os
import io
import time
from datetime import datetime as dt
from base_camera import BaseCamera
# import scipy.misc
import imageio


class Camera(BaseCamera):
    
    video_source = r'C:\Users\Sanskar\Desktop\hmara btp\cow.mp4'
    # video_source = 0

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        thres=0.56
        classNames= []
        classFile = r'C:\Users\Sanskar\Desktop\hmara btp\coco.names'
        with open(classFile,'rt') as f:
            classNames = f.read().rstrip('\n').split('\n')

        configPath = r'C:\Users\Sanskar\Desktop\hmara btp\ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
        weightsPath = r'C:\Users\Sanskar\Desktop\hmara btp\frozen_inference_graph.pb'

        net = cv2.dnn_DetectionModel(weightsPath,configPath)
        net.setInputSize(320,320)
        net.setInputScale(1.0/ 127.5)
        net.setInputMean((127.5, 127.5, 127.5))
        net.setInputSwapRB(True)


        camera = cv2.VideoCapture(Camera.video_source)
        camera.set(3,1280)
        camera.set(4,720)
        camera.set(10,70)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        # construct the argument parser and parse the arguments
        ap = argparse.ArgumentParser()
        ap.add_argument("-c", "--conf", required=True,
            help="path to the JSON configuration file")
        args = vars(ap.parse_args())

        # filter warnings, load the configuration and initialize the Dropbox
        # client
        warnings.filterwarnings("ignore")
        conf = json.load(open(args["conf"]))
        # let camera warm up
        print("[INFO] warming up...")
        time.sleep(conf["camera_warmup_time"])

        # allow the camera to warmup, then initialize the average frame, last
        # uploaded timestamp, and frame motion counter
        avg = None
        lastUploaded = datetime.datetime.now()
        # for waiting 20 sec
        flag= False
        start=dt.now()
        motionCounter = 0
        imgCounter = 0
        
        # capture frames from the camera
        while True:
            # grab the raw NumPy array representing the image and initialize
            # the timestamp and occupied/unoccupied text
            ret, frame = camera.read()
            classIds, confs, bbox = net.detect(frame,confThreshold=thres)
    #print(classIds,bbox)
            label=''
            if len(classIds) != 0:
                for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
                    label=classNames[classId-1].upper()
                    if label=='CAR' or label =='TRUCK' or label=='MOTORCYCLE' or label=='BICYCLE' or label=='BUS' or label=='CAT' or label=='BIRD' or label=='COW' or label=='DOG' or label=='HORSE':

                        cv2.rectangle(frame,box,(0,0,255),1)
                    
                        # print(label)
                        cv2.putText(frame,label,(box[0]+10,box[1]+30),
                            cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),1)

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', frame)[1].tobytes()

            timestamp = datetime.datetime.now()
            text = "No motion detected.."

            # resize the frame, convert it to RGB,
            # and make a grayscale copy and blur it
            frame = cv2.cvtColor(imutils.resize(frame, width=500), cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # if the average frame is None, initialize it
            if avg is None:
                print("[INFO] starting background model...")
                avg = gray.copy().astype("float")
                continue

            # accumulate the weighted average between the current frame and
            # previous frames, then compute the difference between the current
            # frame and running average
            cv2.accumulateWeighted(gray, avg, 0.5)
            frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

            # threshold the delta image, dilate the thresholded image to fill
            # in holes, then find contours on thresholded image
            thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
                cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if imutils.is_cv2() else cnts[0]
            

            # loop over the contours
            for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < conf["min_area"]:
                    continue

                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                if label=='COW' or label=='DOG' or label=='BIRD' or label=='CAT' or label=='HORSE':
                    os.system('pushbullet.sh "'+label+' is trespassing!!!"')

                if w>100 and h>100:
                    start=dt.now()
                text = "Motion Detected!"

            # draw the text and timestamp on the frame
            ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
            cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.35, (0, 0, 255), 1)
            

            # check to see if the room is occupied
            if text == "Motion Detected!":
                # check to see if enough time has passed between uploads
                if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
                    # increment the motion counter
                    motionCounter += 1 
                    flag= True
                    # check to see if the number of frames with consistent motion is
                    # high enough
                    if motionCounter >= conf["min_motion_frames"]:
                        # update the last uploaded timestamp and reset the motion
                        # counter
                        print("[INFO] Motion detected!")
                        
                        # scipy.misc.imsave('./saved_imgs/outfile'+str(imgCounter)+'.jpg', frame)
                        # imageio.imwrite('./saved_imgs/outfile'+str(imgCounter)+'.jpg', frame )
                        # os.system('pushbullet.sh "./saved_imgs/outfile"+str(imgCounter)+".jpg"')

                        imgCounter += 1
                        
                        lastUploaded = timestamp
                        motionCounter = 0
                    # start = dt.now()
            # otherwise, the room is not occupied
            else:
                motionCounter = 0
                end=dt.now()
                val=(end-start).total_seconds()
                print(val)
                if int(val)>= 20 and (label=='CAR' or label =='TRUCK' or label=='MOTORCYCLE' or label=='BICYCLE' or label=='BUS'):
                    imageio.imwrite('./saved_imgs/outfile'+str(imgCounter)+'.jpg', frame )
                    os.system('pushbullet.sh "'+label+' vehicle is standing on your door"')
                    start=dt.now()
                    print("i ran") 