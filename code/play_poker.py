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

from actions import initializeTable, getTableState, screenTable
from Button import Button
#from ScreenItem import DealerButton, Table
from extra_functions import getRandDistrParams

take_actions=False


print('First screen Scan')


table_img = screenTable(library='xlib')
table = initializeTable(table_img)
print('At position: '+str(table.center_pos))

for i in range(60):

    #define the beta distribution parameters, from where the randomness of the agent is drawn
    beta_, alpha_smart, alpha_balanced = getRandDistrParams();

    #wait some time (add randomness)
    time.sleep(1+0.6*beta.rvs(alpha_smart,beta_, size=1)[0])

    print('New screen Scan')
    table_img = screenTable()
   # table_img.show()
    
    #table_img_portion = table_img.crop((2, 2, 80,80))
    #table_img_portion.show()
    fast_fold, fold, check, call, bet, raise_to, dealer_button = getTableState(table_img, table)
    
    
    #see if it is my turn to play
    if(check.is_available or fold.is_available):
        print("### Heros' turn ###")
        #check.moveTo(click=take_actions)
        #fold.moveTo(click=take_actions)
    else:
        pass
        #dealer_button.moveTo(click=False)
      

    #Attempt to locate dealer_button
    #table.locate(table_img = table_img) #box = pyautogui.locate('../data/images/'+table.image_path, table_img, confidence=table.detection_confidence)
    #table.printPosition()


