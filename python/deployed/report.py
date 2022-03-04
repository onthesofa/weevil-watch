#!/usr/bin/env python3

# Bug view by Matt Butler, Harper Adams University 2022

import math
import requests
from picamera.array import PiRGBArray
from picamera import PiCamera
import datetime
from time import sleep
import cv2
import numpy as np
import RPi.GPIO as pio

from email_summary import *
from combo_sense import *
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use('agg')

import gc


url = 'https://mechatron.co.uk/weevils/upload.php'
training_url = 'https://mechatron.co.uk/weevils/upload_training.php'

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (1232, 1232)
# camera.shutter_speed = 2000000
# camera.iso = 600
camera.awb_mode = 'off' #'fluorescent'
camera.awb_gains = 1.5

pio.setmode(pio.BCM)
led15 = 22
pio.setup(led15, pio.OUT)

dateraw= datetime.datetime.now()
datetimeformat = dateraw.strftime("%Y-%m-%d_%H:%M")
print("RPi started taking photos for your timelapse at: " + datetimeformat)

first_run = True

pos = 0 # position in matrix (0 to 24)
harper_image = cv2.imread('Harper.png')
most_weevils_image = harper_image

most_weevils_detected = 0 # to choose 24 hr image to upload
accum_weevil_num = 0 # keep a tally per time period
matrix = np.zeros(shape=(500,500,3))

hours = ['12','13','14','15','16','17','18','19','20','21','22','23','00','01','02','03','04','05','06','07','08','09','10','11']
detections = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
luxs = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
temps = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
humids = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]

now = datetime.datetime.now()
last_H = int(now.strftime("%H"))

def filter_single(img):
   # convert image to grayscale image
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # convert the grayscale image to binary image
    ret,thresh = cv2.threshold(gray_image,127,255,0)   
    light = np.mean(thresh)
    # calculate moments of binary image
    M = cv2.moments(thresh)
    try:     
        # calculate x,y coordinate of center
        cX = int(M["m10"] / (M["m00"] + 1e-5))
        cY = int(M["m01"] / (M["m00"] + 1e-5))  
        unbalance = abs(cX-49)+abs(cY-49) # zero index?
        #print(unbalance)
        #print(light)
        
        if (unbalance < 8) and (light > 200):
            print("single insect")
            return(True)
    except:
        print("bad egg")
        return(False)
    print("multi insect")
    return(False)

def upload_image(np_array, str_fname, extn):
    try:
        
        (flag, img) = cv2.imencode(extn, np_array) 
        print(str_fname)
        files = {'imageFile': (str_fname,img,'multipart/form-data',{'Expires': '0'}) }
        with requests.Session() as s:
            r = s.post(url,files=files)
            print(r.status_code)
            print (r.text)
        del img
    except:
        print('Upload error :(')
        
def upload_training(np_array, str_fname, extn):
    try:
        
        (flag, img) = cv2.imencode(extn, np_array) 
        print(str_fname)
        files= {'imageFile': (str_fname,img,'multipart/form-data',{'Expires': '0'}) }
        with requests.Session() as s:
            r = s.post(training_url,files=files)
            print(r.status_code)
            print (r.text)
        del img
    except:
        print('Upload error :(')

ksize = (7, 7) # kernel for bluring
thresh = 200
params = cv2.SimpleBlobDetector_Params()
# thresholds
params.minThreshold = 115
params.maxThreshold = 135
#params.thresholdStep = 10

# filter by area
params.filterByArea = True
params.minArea = 500
params.maxArea = 10000

# filter by circularity
params.filterByCircularity = False

# filter by convexity
params.filterByConvexity = False

# filter by inertia
#params.filterByInertia = True
#params.minInertiaRatio = 0.01
        
def extract(img_a, img_b, snap_time):
    
    global most_weevils_image # refreshed after 24 hr reporting period
    global most_weevils_detected # to choose 24 hr image to upload
    global accum_weevil_num # keep a tally per time period
    global pos # position to place bug in matrix
    global matrix # of bugs
    
    #cv2.namedWindow("Display a", cv2.WINDOW_NORMAL)
    img_a_grey = cv2.cvtColor(img_a, cv2.COLOR_BGR2GRAY)
    img_a_grey = cv2.blur(img_a_grey, ksize) 
    #cv2.imshow('Display a', img_a)

    #cv2.namedWindow("Display b", cv2.WINDOW_NORMAL)
    img_b_grey = cv2.cvtColor(img_b, cv2.COLOR_BGR2GRAY)
    img_b_grey = cv2.blur(img_b_grey, ksize) 
    #cv2.imshow('Display b', img_b)

    img_diff = cv2.subtract(img_a_grey,img_b_grey)
    img_diff = (255-img_diff)
 
    #cv2.namedWindow("B + W", cv2.WINDOW_NORMAL)
    im_bw = cv2.threshold(img_diff, thresh, 255, cv2.THRESH_BINARY)[1]
    #cv2.imshow('B + W', im_bw)
    
    detector = cv2.SimpleBlobDetector_create(params)

    keypoints = detector.detect(im_bw)
    img_keypoints = cv2.drawKeypoints(img_diff, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    #cv2.namedWindow("Bugs", cv2.WINDOW_NORMAL)
    #cv2.imshow('Bugs', img_keypoints)
    
    img_c = img_b.copy()

    n = 0
    valid_hits = False
    
    for keypoint in keypoints:
        print(keypoint.pt)
        if not ((keypoint.pt[1] < 60) or (keypoint.pt[1] > 1172) or (keypoint.pt[0] < 60) or (keypoint.pt[0] > 1172)):
            n = n + 1
            accum_weevil_num = accum_weevil_num + 1
            cv2.circle(img=img_c, center = (int(keypoint.pt[0]), int(keypoint.pt[1])), radius =50, color =(0,0,255), thickness=10)
            roi = img_b[int(keypoint.pt[1]-50):int(keypoint.pt[1]+50), int(keypoint.pt[0]-50):int(keypoint.pt[0]+50)]
            
            if (filter_single(roi)):
            
                #cv2.imshow("Cropped", roi)
                #cv2.waitKey(0)
                bug_file = snap_time + "(" + str(n) + ")"+ ".png"
                upload_training(roi, bug_file, ".png")
                valid_hits = True
                if (n >= most_weevils_detected):
                    most_weevils_detected = n
                    most_weevils_image = img_c
                    
                x = (pos%5 * 100)
                if pos < 5:
                    y = 0
                elif pos < 10:
                    y = 100
                elif pos < 15:
                    y = 200
                elif pos < 20:
                    y = 300
                elif pos < 25:
                    y = 400
                #print(x)
                #print(y)
                #print()
                matrix[y:y+100,x:x+100] = roi[:,:]
                
                pos = pos + 1
                if (pos > 24):
                    pos = 0
                
            del roi
                
    print(str(n) + " bugs!")
    
    del img_c
    del img_keypoints
    del im_bw
    del img_diff
    del img_a_grey
    del img_b_grey
        
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
        
    if valid_hits:
        f_name = snap_time + "(M" + str(n) + ")" + ".jpg"
        ###### upload_image(img_c, f_name, ".jpg")

def add_date_text(image_to_annotate, annotation):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 1.1
    BLACK = (255,255,255)
    font_color = BLACK
    font_thickness = 2
    text = annotation
    x,y = 10, 30
    img_text = cv2.putText(image_to_annotate, text, (x,y), font, font_size, font_color, font_thickness, cv2.LINE_AA)
    upload_image(img_text, "latest.jpg", ".jpg")
    del img_text

    
gc_start = len(gc.get_objects())


while True:
    
    pio.output(led15, True)
    print("22 on (15)")
    now = datetime.datetime.now()
    snaptime = now.strftime("%Y.%m.%d_%H.%M")
    fname = snaptime + "(Start)" + ".jpg"
    sleep(0.75)
    rawCapture = PiRGBArray(camera)
    camera.capture(rawCapture, format="bgr")
    image_b = rawCapture.array
    del rawCapture
    print("Photo taken")
    pio.output(led15, False)
    print("22 off (15)")
    print(image_b.shape)
    
    if first_run:
        ###### upload_image(image_b, fname, ".jpg")
        image_a = image_b
        first_run = False
        
    upload_image(harper_image,"harper.jpg", ".jpg")
    
    if not first_run:
        extract(image_a, image_b, snaptime)
        image_a = image_b 
    
    # luxs
    lightLevel = int(readLight())
    lux = lightLevel
    time.sleep(0.5)
    temperature,pressure,humidity = readBME280All()
    temp = temperature
    humid = round(humidity, 2)

    add_date_text(image_b, now.strftime("%H:%M %d/%m/%Y") + ' Lux: ' + str(lux) + ', Temp: ' + str(temp) + ' C, RH: ' + str(humid) + '%')
    #print("zzzzzzzzz")

    #print(int(math.ceil(4.2)))
    #print(detections[0])
    '''
    try:
        cv2.imshow("Most weevils", most_weevils_image)
        cv2.waitKey(3000)
    except:
        print("No image of movement yet")
    '''
        
    print("most_weevils_detected = " + str(most_weevils_detected))
    print("accum_weevil_num = " + str(accum_weevil_num))
    
    
    now = datetime.datetime.now()
    H_now = int(now.strftime("%H"))
    if (H_now != last_H):
        print("New hour " + str(H_now))
        ###### DO STUFF HERE!
        write_hr = H_now
        if (write_hr < 13):
            write_hr = write_hr + 11
        else:
            write_hr = write_hr - 13
            
        if (accum_weevil_num > 0):
            detections[write_hr] = int(math.ceil(accum_weevil_num/6))
        else:
            detections[write_hr] = 0
        
        
        # luxs
        lightLevel = int(readLight())
        luxs[write_hr] = lightLevel
        time.sleep(0.5)
        print(luxs)
        
        # temp, humidty
        temperature,pressure,humidity = readBME280All()
        temps[write_hr] = temperature
        humids[write_hr] = round(humidity, 2)
        print(temps)
        print(humids)

        
            
        accum_weevil_num = 0
        print(detections)
        
 
        if (H_now == 12):
            
            # plot weevil activity
            fig = plt.figure()
            plt.bar(hours, detections)

            plt.title('Weevil Activity')
            plt.xlabel('Hour of Day')
            plt.ylabel('Average Movements Detected')

            fig.canvas.draw()

            # Now we can save it to a numpy array.
            data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            bchart = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            
            # plot lux
            fig = plt.figure()
            plt.bar(hours, luxs, color = 'yellow')
            plt.title('Light Intensity')
            plt.xlabel('Hour of Day')
            plt.ylabel('Lux')
            fig.canvas.draw()
            data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            bchart_l = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

            # plot temp
            fig = plt.figure()
            plt.bar(hours, temps, color = 'red')
            plt.title('Temperature (Celsius)')
            plt.xlabel('Hour of Day')
            plt.ylabel('Degrees C')
            fig.canvas.draw()
            data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            bchart_t = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

            # plot humidity
            fig = plt.figure()
            plt.bar(hours, humids, color = 'blue')
            plt.title('Relative Humidity')
            plt.xlabel('Hour of Day')
            plt.ylabel('RH %')
            fig.canvas.draw()
            data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            bchart_h = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            
            del fig
       
            send_email(bchart, bchart_l, bchart_t, bchart_h, most_weevils_image, matrix)
            
            del data
            del bchart
            del bchart_l
            del bchart_t
            del bchart_h
            
            detections = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
            most_weevils_image = cv2.imread('Harper.png')
            most_weevils_detected = 0
            matrix = np.zeros(shape=(500,500,3))
            pos = 0
                
        last_H = H_now

# display the image on screen and wait for a keypress
#cv2.imshow("Image", image)
#cv2.imshow("Image2", image2)
#cv2.waitKey(0)
    print('zzzzzzzz')
    now = datetime.datetime.now()
    last_min = int(now.strftime("%M"))
    #print("Tracked objects start: " + str(gc_start))
    #print("Tracked objects now: " + str(len(gc.get_objects())))
    
    while ((int(now.strftime("%M"))%10) != 0) or ((int(now.strftime("%M")) == last_min)):
        sleep(1)
        #print(last_min)
        #print(int(now.strftime("%M")))
        #print(((int(now.strftime("%M"))%10) != 0))
        #print(int(now.strftime("%M") == last_min))
        now = datetime.datetime.now()
    
    gc.collect()
              
    #sleep(600)