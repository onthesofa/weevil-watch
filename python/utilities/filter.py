# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 15:36:49 2022

@author: 00751570
run to filter images in pwd by momentum
"""
import cv2
import os
import datetime
import numpy as np


dir_list = os.listdir()
now = datetime.datetime.now()
outDir = "filtered/" + now.strftime("%Y-%m-%d")
if not os.path.exists(outDir):
    os.makedirs(outDir)

# print(dir_list)

def filter_by_momentum(file_name):
    img = cv2.imread(file_name)

    # convert image to grayscale image
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # convert the grayscale image to binary image
    ret,thresh = cv2.threshold(gray_image,127,255,0)
    
    light = np.mean(thresh)

    # calculate moments of binary image
    M = cv2.moments(thresh)

    try:     
        # calculate x,y coordinate of center
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    
        unbalance = abs(cX-49)+abs(cY-49) # zero index?
        print(unbalance)
        print(light)
        
        if (unbalance < 8) and (light > 200) :
            cv2.imwrite(outDir + '/' + file_name,img)
    except:
        print("bad egg")



for fname in dir_list:
    if fname[-3:] == 'png':
        print(fname)
        filter_by_momentum(fname)
    
    


"""

# put text and highlight the center
cv2.circle(img, (cX, cY), 5, (255, 255, 255), -1)
cv2.putText(img, str(unbalance), (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

# display the image
cv2.imshow("Image", img)
cv2.waitKey(0)

"""