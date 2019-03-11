#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 17:29:21 2019

@author: cyril
"""
from PIL import Image #PIL

import random
import pyautogui
import time
from scipy.stats import beta
from Button import Button
from ScreenItem import Table
from DealerButton import DealerButton
from Card import Card, HeroCards
import numpy as np
import sys 

def screenTable(library='xlib'):
    if (library=='xlib'):
        from Xlib import display, X
        ##Get screenshot of the table##
        width,height = int((1/2)*pyautogui.size().width),int((3/4)*pyautogui.size().height)
        dsp = display.Display()
        root = dsp.screen().root
        raw = root.get_image(0, 0, width, height, X.ZPixmap, 0xffffffff)
        table_img = Image.frombytes("RGB", (width, height), raw.data, "raw", "BGRX")#.convert('L')
       # print(table_img)
        return table_img
    elif (library=='pyqt'):
        from PyQt4.QtGui import QPixmap, QApplication
        from PyQt4.Qt import QBuffer, QIODevice
        import io
        app = QApplication(sys.argv)
        buffer = QBuffer()
        buffer.open(QIODevice.ReadWrite)
        QPixmap.grabWindow(QApplication.desktop().winId()).save(buffer, 'png')
        strio = io.BytesIO()
        strio.write(buffer.data())
        buffer.close()
        del app
        strio.seek(0)
        table_img = Image.open(strio)
        width,height = int((1/2)*pyautogui.size().width),int((3/4)*pyautogui.size().height)
        table_img = table_img.crop((0,0,width,height))
       # print(table_img)
        return table_img
        
    else:
        print("The library: "+library+" can't be used here")


def initializeTable(table_img):        
    table = Table(id_='Table', image_path = 'table.png', detection_confidence=0.5)
    table.locate(table_img)
    
    return table

def findAllOpenCards(table, table_img):
    

    card_colors = ['heart','diamond','club','spade']
    card_colors = ['club','diamond']
    cards = []
    for i, card_color in enumerate(card_colors):
        #pyautogui.locate('../data/images/cards/card_'+card_color+'.png', table_img, confidence=0.9)
        #try:
            for j, box in enumerate(pyautogui.locateAll('../data/images/cards/card_'+card_color+'.png', table_img, confidence=0.8)):
                print(box)
                cards.append(Card(id_='card_'+card_color+'_'+str(j), color = card_color[0], box= box, table=table, table_img=table_img))
        #except:
         #   pass

    cards.sort(key=lambda x: x.box.left)
    cards.sort(key=lambda x: x.isHeroCard, reverse=True)
    
    #print(cards[0].value)
    print("There are : "+str(len(cards)))
    if(len(cards)>=2):
        print("## Hero has: "+cards[0].value+ cards[0].color+ ", "+cards[1].value+ cards[1].color+ " ##")
    if(len(cards)>=5):
        print("## Flop is: "+cards[2].value+ cards[2].color+", "+cards[3].value+ cards[3].color+", "+cards[4].value+ cards[4].color+ " ##")
    if(len(cards)>=6):
        print("## Turn is: "+cards[5].value+ cards[5].color+" ##")
    if(len(cards)>=7):
        print("## River is: "+cards[6].value+ cards[6].color+" ##")
    return cards
    

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

    #cards =['2','3','4','5','6','7','8','9','J','Q','K','A']
    #for card in cards:
    #card_2 = Card(id_='card_2', image_path= 'card_2',detection_confidence=0.65)
    #card_2.locate(table_img)
    #card_3 = Card(id_='card_3', image_path= 'card_3',detection_confidence=0.65)
    #card_3.locate(table_img)
    #card_4 = Card(id_='card_4', image_path= 'card_4.png',detection_confidence=0.9)
    #card_4.locate(table_img)
    #card_5 = Card(id_='card_5', image_path= 'card_5.png',detection_confidence=0.9)
    #card_5.locate(table_img)
    #card_spade = Card(id_='card_spade', image_path= 'card_spade.png',detection_confidence=0.9)
    #card_spade.locate_all(table_img)
    #print(card_spade.isHeroCard(table))
    #card_diamond = Card(id_='card_diamond', image_path= 'card_diamond.png',detection_confidence=0.9)
    #card_diamond.locate(table_img)
    #print(card_spade.isHeroCard())
    #card_heart = Card(id_='card_heart', image_path= 'card_heart.png',detection_confidence=0.9)
    #card_heart.locate(table_img)
    #card_club = Card(id_='card_club', image_path= 'card_club.png',detection_confidence=0.9)
    #card_club.locate(table_img)
    findAllOpenCards(table, table_img)
    #card_club.getCardValue()
    
    #card_test = Card(id_='test', image_path= 'test.png',detection_confidence=0.9)
    #card_test.locate(table_img)
    
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