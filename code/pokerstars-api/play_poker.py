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

from screen_api import initializeTable, updateTableState, screenTable
from Button import Button
#from ScreenItem import DealerButton, Table
from extra_functions import getRandDistrParams

import constants
import glob_file


constants.init()
glob_file.init()

do_moves = False
do_clicks = False
click_time = 'random'



initializeTable()

for i in range(60):

    #define the beta distribution parameters, from where the randomness of the agent is drawn
    beta_, alpha_smart, alpha_balanced = getRandDistrParams();

    #wait some time (add randomness)
    time.sleep(0.2+0.6*beta.rvs(alpha_smart,beta_, size=1)[0])
    updateTableState()

    #see if it is my turn to play
    if(glob_file.check.is_available or glob_file.fold.is_available):
        print("-> Heros' turn")

        hero_cards = [glob_file.cards[0].value,glob_file.cards[1].value]
        aggressive_cards = ['A','K','Q','J']

        if(any(x in hero_cards for x in aggressive_cards) and do_moves):
            """going for a bet"""
            glob_file.bet_sizer.moveTo(click=do_clicks)
            if(do_clicks):
                #take short break before clicking
                if(click_time=='random'):
                    time.sleep(int(random.choice('111'))*0.2*beta.rvs(alpha_smart,beta_, size=1)[0])
                pyautogui.click()
                if(click_time=='random'):
                    time.sleep(int(random.choice('111'))*0.2*beta.rvs(alpha_smart,beta_, size=1)[0])
                pyautogui.click()
            if(bet.is_available):
                glob_file.bet.moveTo(click=do_clicks)
            elif(raise_to.is_available):
                glob_file.raise_to.moveTo(click=do_clicks)
            else:
                glob_file.fold.moveTo(click=do_clicks)

        else:
            if(do_clicks):
                glob_file.dealer_button.moveTo(click=False)
            pass
