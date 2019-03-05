#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 17:29:21 2019

@author: cyril
"""

import random
import pyautogui
import time
from scipy.stats import beta

def move_to_button(button_):    
    print('test')
    #print('Handling movement');
    #define the beta distribution parameters, from where the randomness of the agent is drawn
    beta_=random.uniform(0.1,5);
    alpha_smart=random.uniform(beta_,5);
    alpha_balanced=random.uniform(0.1,5);
    
    #define aimed location (with randomness)
    aimed_button = button_
    x_aimed = aimed_button.left+beta.rvs(alpha_balanced,beta_, size=1)[0]*aimed_button.width
    y_aimed = aimed_button.top+beta.rvs(alpha_balanced,beta_, size=1)[0]*aimed_button.height
    #define time to move (between 0.1 and 2 seconds)
    time_to_move = 0.1+2.4*beta.rvs(alpha_smart,beta_, size=1)[0]
    #define the easing function
    easing_function_select = beta.rvs(alpha_balanced,beta_, size=1)[0]*5
    if(easing_function_select<=1):
        #easing_function = pyautogui.easeInBounce;
        easing_function = pyautogui.easeInQuad;
    elif(easing_function_select<=2):
        easing_function = pyautogui.easeInQuad;
    elif(easing_function_select<=3):
        easing_function = pyautogui.easeInOutQuad;
    elif(easing_function_select<=4):
        easing_function = pyautogui.easeOutQuad;
    elif(easing_function_select<=5):
        #easing_function = pyautogui.easeInElastic;   
        easing_function = pyautogui.easeOutQuad;
    pyautogui.moveTo(x_aimed, y_aimed, time_to_move, easing_function)  
    #take short break before clicking
    time.sleep(int(random.choice('011'))*0.8*beta.rvs(alpha_balanced,beta_, size=1)[0])
    #time.sleep(int(time_to_move))
    pyautogui.click()
    print('Succesfuly handled movement');
    return