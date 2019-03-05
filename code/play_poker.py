#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 09:15:36 2019

@author: cyril
"""
from Xlib import display, X
from PIL import Image #PIL
import time
from skimage import feature
import matplotlib.pyplot as plt
from skimage.color import rgb2gray
import numpy as np
import colorsys
import pyautogui
import random
from scipy.stats import beta

from actions import move_to_button
from Button import Button

take_actions=False


for i in range(60):

    #define the beta distribution parameters, from where the randomness of the agent is drawn
    beta_=random.uniform(0.1,5);
    alpha_smart=random.uniform(beta_,5);
    alpha_balanced=random.uniform(0.1,5);

    #wait some time (for previous action to take effect, and add randomness)
    time.sleep(1+0.6*beta.rvs(alpha_smart,beta_, size=1)[0])
    print('New screen Scan')

    ##Get screenshot of the table##
    W,H = int((1/2)*pyautogui.size().width),int((3/4)*pyautogui.size().height)
    dsp = display.Display()
    root = dsp.screen().root
    raw = root.get_image(0, 0, W,H, X.ZPixmap, 0xffffffff)
    table_img = Image.frombytes("RGB", (W, H), raw.data, "raw", "BGRX").convert('L')

    menu_fast_fold, menu_fold, menu_check = None, None, None;

    fast_fold = Button(id_='Fast_fold', image_path='menu_fast_fold.png', detection_confidence=0.8)
    fold = Button(id_='Fold', image_path='menu_fold.png', detection_confidence=0.8)
    check = Button(id_='Check', image_path='menu_check.png', detection_confidence=0.8)
    call = Button(id_='Call', image_path='menu_call.png', detection_confidence=0.65)
    raise_to = Button(id_='Raise_to', image_path='menu_raise_to.png', detection_confidence=0.7)
    bet = Button(id_='Bet', image_path='menu_bet.png', detection_confidence=0.65)

    buttons = [fast_fold, fold, check, call, raise_to]
    #buttons = [call, raise_to]

    #Read all buttons
    for button in buttons:
        ##See if cards are dealt
        try:
            #Attempt to locate fast_fold_button
            button.box = pyautogui.locate('../data/images/'+button.image_path, table_img, confidence=button.detection_confidence)
            print('Button : "'+ button.id +'" available')
            if(take_actions):
                #print('tets')
                if(button.id=='Fast_fold'):
                    #print('test')
                    print('Moving to: "'+button.id+'"')
                    move_to_button(button.box)

        except:
            pass
            #print('') 


   


#img_gray = rgb2gray(np.array(list(image.getdata())))

#startButton = pyautogui.locateOnScreen('../screenshots/dealer_button.png', region=(0,0,970,810), confidence=0.6)

#img_array = np.array(img)

#img_hsv = colorsys.rgb_to_hsv(img_array[1]/255.,img_array[2]/255.,img_array[3]/255.)

#brain_cont_canny = feature.canny(img_array, sigma=1, low_threshold = 20, high_threshold = 60)


#ax.imshow(brain_cont_canny,cmap='gray')
#plt.show()

#fig, ax = plt.subplots(1, 1, figsize=(12, 12))
#img_tresh = (img_array>240)
#ax.imshow(img_tresh, cmap='gray')