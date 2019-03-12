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
    num_displays=1
    if (library=='xlib'):
        from Xlib import display, X
        ##Get screenshot of the table##
        width,height = int((1/2)*pyautogui.size().width/num_displays),int((3/4)*pyautogui.size().height)
        dsp = display.Display()
        root = dsp.screen().root
        raw = root.get_image(0, 0, width, height, X.ZPixmap, 0xffffffff)
        table_img = Image.frombytes("RGB", (width, height), raw.data, "raw", "BGRX").convert('RGB')
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
        width,height = int((1/2)*pyautogui.size().width/num_displays),int((3/4)*pyautogui.size().height)
        table_img = table_img.crop((0,0,width,height))
       # print(table_img)
        return table_img
        
    else:
        print("The library: "+library+" can't be used here")


def initializeTable(table_img):        
    table = Table(id_='Table', image_path = 'table.png', detection_confidence=0.5)
    table.search(table_img)
    
    
    
    
    
    return table

def findAllOpenCards(table, table_img):
    
    #table_img.show()
    
    #hero_card_1 = CardHolder(id_='hero_card_1', image_path='AAA.png', detection_confidence=0.7)
    #hero_card_2 = Button(id_='hero_card_2', image_path='AAA.png', detection_confidence=0.7)
    card_colors = ['heart','diamond','club','spade']
    #card_colors = ['club','diamond']
    cards = []
    known_positions=[]
    for i, card_color in enumerate(card_colors):
        #pyautogui.locate('../data/images/cards/card_'+card_color+'.png', table_img, confidence=0.9)
        #try:
            for j, box in enumerate(pyautogui.locateAll('../data/images/cards/card_'+card_color+'.png', table_img, confidence=0.9)):
                known=False
                for known_position in known_positions:
                    #avoid spotting twice the same
                    if((box.left>(known_position["left"]-box.width/2) and box.left<(known_position["left"]+box.width/2)) and (box.top>(known_position["top"]-box.height/4) and box.top<(known_position["top"]+box.height/4))): #
                        known=True
                        break
                
                
                if(not(known)):
                    #print(box)
                    known_positions.append({'left':box.left,'top':box.top})
                    new_card =Card(id_='card_'+card_color+'_'+str(j), color = card_color[0], box= box, table=table, table_img=table_img)
                    cards.append(new_card)
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
    dealer_button = DealerButton(id_='Dealer', image_path='dealer_button.png', detection_confidence = 0.8)
    
    screenItems = [fast_fold, fold, check, call, bet, raise_to, dealer_button]
    
    print('created buttons')
    #Read all buttons
    for screenItem in screenItems:
        if(not(screenItem.hasKnownLocation)):
            screenItem.search(table_img)
        else:
            screenItem.update(table_img)
    print('searched buttons')
    #dealer_button = DealerButton(id_='Dealer', image_path='dealer_button.png', detection_confidence = 0.8)
    #dealer_button.search(table_img)
    #dealer_button.getPlayerId(nb_players = 6, table = table)

    findAllOpenCards(table, table_img)
    #card_club.getCardValue()
    
    #card_test = Card(id_='test', image_path= 'test.png',detection_confidence=0.9)
    #card_test.locate(table_img)
    
    return fast_fold, fold, check, call, bet, raise_to, dealer_button
    


