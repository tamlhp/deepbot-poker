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
from Card import Card
import numpy as np
import sys 
from extra_functions import itemExists
import os
from Player import Player

all_cards_found = False
all_players_found = False
players = []
cards = []

def initializeTable(table_img):        
    table = Table(id_='Table', image_path = 'table.png', detection_confidence=0.5)
    table.search(table_img)

    
    #Creating buttons
    global fast_fold
    fast_fold = Button(id_='Fast_fold', image_path='menu_fast_fold.png', detection_confidence=0.8)
    global fold
    fold = Button(id_='Fold', image_path='menu_fold.png', detection_confidence=0.8)
    global check
    check = Button(id_='Check', image_path='menu_check.png', detection_confidence=0.8)
    global call
    call = Button(id_='Call', image_path='menu_call.png', detection_confidence=0.65)
    global raise_to
    raise_to = Button(id_='Raise_to', image_path='menu_raise_to.png', detection_confidence=0.7)
    global bet
    bet = Button(id_='Bet', image_path='menu_bet.png', detection_confidence=0.65)
    global dealer_button
    dealer_button = DealerButton(id_='Dealer_button', image_path='dealer_button.png', detection_confidence = 0.8, table=table)
    global bet_sizer
    bet_sizer = Button(id_='Bet_sizer', image_path='bet_sizer.png', detection_confidence = 0.9)

    #print('Created buttons')
    
    #Creating card relative variable
    global all_cards_found
    all_cards_found = False
    global cards
    cards = []
    
    #Creating player relative variables
    global all_players_found
    all_players_found = False
    global players
    players = []
    return table

def updateTableState(table_img, table):        
 
    screenItems = [fast_fold, fold, check, call, bet, raise_to, dealer_button, bet_sizer]
    

    #Search or update all buttons
    for screenItem in screenItems:
        if(not(screenItem.hasKnownLocation)):
            screenItem.search(table_img)
        else:
            screenItem.update(table_img)

    #print(all_cards_found)
    #Search for or update all cards
    if (not(all_cards_found)):
        searchAllOpenCards(table, table_img)
    else:
        for card in cards:
            card.update()
    printCardsInfo()  

    #print(all_players_found)
    #Search for or update all players    
    if(not(all_players_found)):
        searchAllPlayers(table_img)
    else:
        for player in players:
            player.update(table_img)
    printPlayersInfo()

    return cards, players, fast_fold, fold, check, call, bet, raise_to, dealer_button, bet_sizer





def searchAllOpenCards(table, table_img):
    global all_cards_found
    all_cards_found = False
    global cards
    cards=[]
    
    card_colors = ['heart','diamond','club','spade']
    known_positions=[]
    for i, card_color in enumerate(card_colors):
        #pyautogui.locate('../data/images/cards/card_'+card_color+'.png', table_img, confidence=0.9)
        try:
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
        except:
            pass
    
    cards.sort(key=lambda x: x.box.left)
    cards.sort(key=lambda x: x.isHeroCard, reverse=True)

    
    #print("There are : "+str(len(cards))+ " cards")
    if(len(cards)>=2):
        if(cards[0].box.left>cards[1].box.left):
            card_0, card_1 = cards[1], cards[0]
            cards[1], cards[0] = card_1, card_0
    if(len(cards)==7):
        #All cards were found, creating classes for speedup
        all_cards_found = True
        for i,card in enumerate(cards):
            card.setId(i)
        print("# All cards found and classes created #")
    if(len(cards)>7):
        print("[Warning] Too many cards spotted!")
        
    return cards
    




def searchAllPlayers(table_img):
    global all_players_found
    all_players_found=False    
    global players
    players = []
    player_holder_path="../data/images/player_holder/"
    player_boxes=[]

    known_positions=[]

    #players_found=0
    for file in os.listdir(player_holder_path):
        #print(file)
        for j, box in enumerate(pyautogui.locateAll(player_holder_path+file, table_img, confidence=0.95)):
            known=False
            for known_position in known_positions:
                #avoid spotting twice the same
                if((box.left>(known_position["left"]-10) and box.left<(known_position["left"]+10)) and (box.top>(known_position["top"]-10) and box.top<(known_position["top"]+10))): #
                    known=True
                    break
                
            if(not(known)):            
                player_boxes.append(box)
                known_positions.append({'left':box.left,'top':box.top})
    
    if(len(player_boxes)<6):
        print('[Warning] Only '+str(len(player_boxes))+" players found")

    elif len(player_boxes)==6:
        player_boxes.sort(key=lambda box: box.left)
        player_boxes.sort(key=lambda box: box.top, reverse=True)
        player_2, player_3,player_5 = player_boxes[3], player_boxes[5], player_boxes[2]
        player_boxes[2], player_boxes[3], player_boxes[5] = player_2, player_3, player_5
        #print(player_boxes)
        for i, box in enumerate(player_boxes):
            players.append(Player(id_=i, box=box, table_img=table_img))
        
        all_players_found = True
        print("# All players found and classes created #")
        
    else:
        print("[Warning] Found too many players")
        pass



    return players


def printCardsInfo():
    if(len(cards)>=2):
        print("-> Hero has: "+cards[0].value+ cards[0].color+ ", "+cards[1].value+ cards[1].color+ "")
    if(len(cards)>=5):
        print("Flop is: "+cards[2].value+ cards[2].color+", "+cards[3].value+ cards[3].color+", "+cards[4].value+ cards[4].color+ "")
    if(len(cards)>=6):
        print("Turn is: "+cards[5].value+ cards[5].color+"")
    if(len(cards)==7):
        print("River is: "+cards[6].value+ cards[6].color+"")
    return cards

def printPlayersInfo():
    players_playing = []
    for player in players:
        if player.is_playing:
            players_playing.append(player.id)
    print("-> Currently active players are: "+ str(players_playing).strip('[]'))

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


