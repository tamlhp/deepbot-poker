#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 09:15:36 2019

@author: cyril
"""
from Xlib import display, X
from PIL import Image #PIL
import time
import sys
sys.path.insert(0, '../poker-simul')
from skimage import feature
import matplotlib.pyplot as plt
from skimage.color import rgb2gray
import numpy as np
import colorsys
import pyautogui
import random
from scipy.stats import beta

from screen_api import initializeTable, updateTableState, screenTable, takeAction
from Button import Button
from game_state_formatter import format_screen_info, write_hero_action
from extra_functions import getRandDistrParams
from bot_PStratBot import PStratBot

import constants
import glob_file



constants.init()
glob_file.init()

glob_file.do_moves = True
glob_file.do_clicks = True
click_time = 'random'

my_verbose = True

"""###SEARCHING AND INITIALIZING TABLE###"""
initializeTable()
#update state once
updateTableState()
#Initializing bot strategy
p_strat_bot = PStratBot()

isHeroTurn = True

while(True):

    #define the beta distribution parameters, from where the randomness of the agent is drawn
    beta_, alpha_smart, alpha_balanced = getRandDistrParams();

    #wait some random time
    time.sleep(0.1+0.3*beta.rvs(alpha_smart,beta_, size=1)[0])
    
    #new table scan
    #print('\n### New screen Scan ###')
    table_img = screenTable(library='xlib')
    glob_file.check.update(table_img)
    glob_file.fold.update(table_img)

    #see if it is my turn to play
    if(glob_file.check.is_available or glob_file.fold.is_available):
        print("-> Heros' turn")
        
        """#### UPDATE TABLE STATE ####"""
        updateTableState()
        
        """### FORMAT SCREEN INFO FOR POKER ENGINE###"""
        format_screen_info()
        
        """###QUERY ACTION FROM BOT###"""
        action, amount = p_strat_bot.declare_action(valid_actions = glob_file.valid_actions, 
                                                    hole_card = glob_file.hole_card, 
                                                    round_state = glob_file.round_state)
        
        write_hero_action(action, amount)
        
        print('#TEST ZONE#')
        print('Chosen action: '+ str(action))
        print('Chosen amount: ' + str(amount))
        
        
        if glob_file.do_moves:
            takeAction(action,amount)
        isHeroTurn = True
        
    else:
        if isHeroTurn==True:
            print("-> Not Hero's turn, waiting")
        isHeroTurn = False

        
        """

        hero_cards = [glob_file.cards[0].value,glob_file.cards[1].value]
        aggressive_cards = ['A','K','Q','J']

        if(any(x in hero_cards for x in aggressive_cards) and do_moves):
            #going for a bet
            glob_file.bet_sizer.moveTo(click=do_clicks)
            if(do_clicks):
                #take short break before clicking
                if(click_time=='random'):
                    time.sleep(int(random.choice('111'))*0.2*beta.rvs(alpha_smart,beta_, size=1)[0])
                pyautogui.click()
                if(click_time=='random'):
                    time.sleep(int(random.choice('111'))*0.2*beta.rvs(alpha_smart,beta_, size=1)[0])
                pyautogui.click()
            if(glob_file.bet.is_available):
                glob_file.bet.moveTo(click=do_clicks)
            elif(glob_file.raise_to.is_available):
                glob_file.raise_to.moveTo(click=do_clicks)
            else:
                glob_file.fold.moveTo(click=do_clicks)

        else:
            if(do_clicks):
                glob_file.dealer_button.moveTo(click=False)
            pass
        """
        """
        ##TODO
        print(glob_file.cards[0])
        print('why not calling __str__')
        """
        

