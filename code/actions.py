#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 17:29:21 2019

@author: cyril
"""
from Xlib import display, X
from PIL import Image #PIL

import random
import pyautogui
import time
from scipy.stats import beta
from Button import Button
from ScreenItem import Table
from DealerButton import DealerButton

def screenTable():
        ##Get screenshot of the table##
    W,H = int((1/2)*pyautogui.size().width),int((3/4)*pyautogui.size().height)
    dsp = display.Display()
    root = dsp.screen().root
    raw = root.get_image(0, 0, W,H, X.ZPixmap, 0xffffffff)
    table_img = Image.frombytes("RGB", (W, H), raw.data, "raw", "BGRX").convert('L')
    return table_img

def initializeTable(table_img):        
    table = Table(id_='Table', image_path = 'table.png', detection_confidence=0.5)
    table.locate(table_img)
    
    return table



def getTableState(table_img, table):        
    #All buttons
    fast_fold = Button(id_='Fast_fold', image_path='menu_fast_fold.png', detection_confidence=0.8)
    fold = Button(id_='Fold', image_path='menu_fold.png', detection_confidence=0.8)
    check = Button(id_='Check', image_path='menu_check.png', detection_confidence=0.8)
    call = Button(id_='Call', image_path='menu_call.png', detection_confidence=0.65)
    raise_to = Button(id_='Raise_to', image_path='menu_raise_to.png', detection_confidence=0.7)
    bet = Button(id_='Bet', image_path='menu_bet.png', detection_confidence=0.65)
    menu = [fast_fold, fold, check, call, bet, raise_to]
    
    #Read all buttons
    for button in menu:
        button.locate(table_img)
    dealer_button = DealerButton(id_='Dealer', image_path='dealer_button.png', detection_confidence = 0.8)
    dealer_button.locate(table_img)
    dealer_button.getPlayerId(nb_players = 6, table = table)
    return fast_fold, fold, check, call, bet, raise_to, dealer_button
    



def move_to_button(button_):    
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
    #time.sleep(int(random.choice('011'))*0.8*beta.rvs(alpha_balanced,beta_, size=1)[0])
    #time.sleep(int(time_to_move))
    #pyautogui.click()
    print('Succesfuly handled movement');
    return