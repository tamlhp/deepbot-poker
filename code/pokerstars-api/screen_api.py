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
from Table import Table
from DealerButton import DealerButton
from Card import Card
from Box import Box
import numpy as np
import sys
from extra_functions import itemExists, computeBoxAngle
import os
from functools import reduce

from Player import Player
from NumberContainer import NumberContainer
from Number import Number

import constants
import glob_file

def initializeTable():
    table_found = False
    while(not(table_found)):
        print('Looking for table')
        table_img = screenTable(library='xlib')
        glob_file.table.update(table_img)
        if(not(glob_file.table.never_spotted)):
            table_found=True
            glob_file.dealer_button.set_relevant_box(glob_file.table.box)
            glob_file.dealer_button.set_table_center(glob_file.table.center_pos)
            print('Found and initialized table at position: '+str(glob_file.table.center_pos))
        else:
            time.sleep(1)


    #num_container = NumberContainer(id_='Number_container', image_file=None, detection_confidence = constants.NUMBERS_BET_DET_CONFIDENCE)
    #num_container.search(table_img)
    return

def updateTableState():

    #new table scan
    print('\n### New screen Scan ###')
    table_img = screenTable(library='xlib')

    unique_screen_items = [glob_file.fast_fold, glob_file.fold, glob_file.check, glob_file.call,
        glob_file.bet, glob_file.raise_to, glob_file.bet_sizer, glob_file.bet_value_box, glob_file.dealer_button]

    #Search or update all buttons
    for screen_item in unique_screen_items:
        screen_item.update(table_img)

    #Search for or update all cards
    if (not(glob_file.all_cards_found)):
        searchAllOpenCards(table_img)
    else:
        for card in glob_file.cards:
            card.update(table_img)
    printCardsInfo()

    #Search for or update all players
    if(not(glob_file.all_players_found)):
        searchAllPlayers(table_img)
    else:
        for player in glob_file.players:
            player.update(table_img)
    glob_file.players[0].set_availability(availability = isHeroAvailable())
    printPlayersInfo()


    searchAllBets(table_img)
    printBetsInfo()

    return

def searchAllOpenCards(table_img):

    glob_file.all_cards_found = False
    glob_file.cards=[]

    card_colors = ['heart','diamond','club','spade']
    known_positions=[]
    for i, card_color in enumerate(card_colors):
        if(True):
            for j, box in enumerate(pyautogui.locateAll(constants.CARD_PATH+card_color+'.png', table_img, confidence=constants.CARD_DET_CONFIDENCE)):
                known=False
                for known_position in known_positions:
                    #avoid spotting twice the same
                    if((box.left>(known_position["left"]-box.width/2) and box.left<(known_position["left"]+box.width/2)) and (box.top>(known_position["top"]-box.height/4) and box.top<(known_position["top"]+box.height/4))): #
                        known=True
                        break


                if(not(known)):
                    known_positions.append({'left':box.left,'top':box.top})
                    new_card =Card(id_='card_'+card_color+'_'+str(j), color = card_color[0], box= box, table_img = table_img)
                    glob_file.cards.append(new_card)
        else:
            pass

    glob_file.cards.sort(key=lambda x: x.box.left)
    glob_file.cards.sort(key=lambda x: x.isHeroCard, reverse=True)


    #print("There are : "+str(len(cards))+ " cards")
    if(len(glob_file.cards)>=2):
        if(glob_file.cards[0].box.left>glob_file.cards[1].box.left):
            card_0, card_1 = glob_file.cards[1], glob_file.cards[0]
            glob_file.cards[1], glob_file.cards[0] = card_1, card_0
    if(len(glob_file.cards)==7):
        #All cards were found, creating classes for speedup
        glob_file.all_cards_found = True
        for i,card in enumerate(glob_file.cards):
            card.setId(i)
        print("# All cards found and classes created #")
    if(len(glob_file.cards)>7):
        print("[Warning] Too many cards spotted!")

    return


def searchAllPlayers(table_img):
    glob_file.all_players_found=False
    glob_file.players = []
    player_boxes=[]

    known_positions=[]

    #players_found=0
    for file in os.listdir(constants.PLAYER_IMAGE_PATH):
        for j, box in enumerate(pyautogui.locateAll(constants.PLAYER_IMAGE_PATH+file, table_img, confidence=constants.PLAYER_DET_CONFIDENCE)):
            #print(box)
            known=False
            for known_position in known_positions:
                #avoid spotting twice the same
                if((box.left>(known_position["left"]-10) and box.left<(known_position["left"]+10)) and (box.top>(known_position["top"]-10) and box.top<(known_position["top"]+10))): #
                    known=True
                    break

            if(not(known)):
                player_boxes.append(box)
                known_positions.append({'left':box.left,'top':box.top})

    if(len(player_boxes)==constants.NB_PLAYERS):
        glob_file.all_players_found = True
        print("# All players found and classes created #")

    if(len(player_boxes)<=constants.NB_PLAYERS):
        print(str(len(player_boxes))+" players found")
        #for i in range(constants.NB_PLAYERS-len(player_boxes)):
        #    player_boxes.append(Box(0,0,0,0))
    #elif len(player_boxes)==constants.NB_PLAYERS:
        
        player_boxes.sort(key=lambda box: computeBoxAngle(box, glob_file.table.center_pos), reverse = True)
       #player_boxes.sort(key=lambda box: box.top, reverse=True)
       # player_2, player_3,player_5 = player_boxes[3], player_boxes[5], player_boxes[2]
       # player_boxes[2], player_boxes[3], player_boxes[5] = player_2, player_3, player_5
        for i, box in enumerate(player_boxes):
            #computeBoxAngle(box, glob_file.table.center_pos)
            glob_file.players.append(Player(id_=i, image_file_path = constants.HOLE_CARDS_IMAGE,
            detection_confidence= constants.HOLE_CARDS_DET_CONFIDENCE, player_box=box, table_img=table_img))

    else:
        print("[Warning] Found too many players")
        pass
    return



def searchAllBets(table_img):
    glob_file.all_bet_containers_found=False
    glob_file.bet_containers = []
    numbers_list = []
    for player in glob_file.players: player.bet_value = 0
    
    table_img_portion = table_img #table_img.crop((self.box.left-100,self.box.top-100,self.box.left+self.box.width+100,self.box.top+self.box.height+100))
    try:
        #Attempt to locate bet
        for i, file in enumerate(range(10)): #os.listdir(constants.NUMBERS_BET_PATH)
            file = str(i)+'.png'
            for j, box in enumerate(pyautogui.locateAll(constants.NUMBERS_BET_PATH+file, table_img_portion, confidence=constants.NUMBERS_BET_DET_CONFIDENCE)):
                if(box!=None):
                    numbers_list.append(Number(value=i, box=box))
                else:
                    pass
    except:
        pass
    numbers_list.sort(key=lambda number: number.left)
    numbers_list.sort(key=lambda number: number.top)
    #print([number.value for number in numbers_list])

    bet_container_id = 0
    for i in range(len(numbers_list)):
        if(i==0):
            number = numbers_list[i]
            glob_file.bet_containers.append(NumberContainer(id_=bet_container_id, type = 'BET'))
            glob_file.bet_containers[bet_container_id].addNumber(number)
        else:
            previous_number =  numbers_list[i-1]
            number = numbers_list[i]

            if (previous_number.left)<=number.left and (previous_number.left+20)>=number.left and previous_number.top==number.top:
                glob_file.bet_containers[bet_container_id].addNumber(number)
            else:
                bet_container_id+=1
                glob_file.bet_containers.append(NumberContainer(id_=bet_container_id, type = 'BET'))
                glob_file.bet_containers[bet_container_id].addNumber(number)

    #print(glob_file.players[0].center_pos)
    for bet_container in glob_file.bet_containers:
        bet_container.computeValue()
        #print(bet_container.value)
        bet_container.attributeEntity(glob_file.players, glob_file.table.center_pos)
        #if bet_container.corresponding_entity!='POT':
        #    glob_file.players[bet_container.corresponding_entity].bet_value = bet_container.value

    glob_file.bet_containers.sort(key=lambda x: -1 if x.corresponding_entity == 'POT' else x.corresponding_entity)

    if(len(glob_file.bet_containers)==constants.NB_PLAYERS):
        glob_file.all_bet_containers_found = True

    return


def printCardsInfo():
    #still not found all cards
    if(len(glob_file.cards)<=6):
        if(len(glob_file.cards)>=2):
            print("-> Hero has: "+glob_file.cards[0].value+ glob_file.cards[0].color+ ", "+glob_file.cards[1].value+ glob_file.cards[1].color+ "")
        if(len(glob_file.cards)>=5):
            print("Flop is: "+glob_file.cards[2].value+ glob_file.cards[2].color+", "+glob_file.cards[3].value+ glob_file.cards[3].color+", "+glob_file.cards[4].value+ glob_file.cards[4].color+ "")
        if(len(glob_file.cards)==6):
            print("Turn is: "+glob_file.cards[5].value+ glob_file.cards[5].color+"")
    ##all cards were found
    elif(len(glob_file.cards)==7):
        available_cards = [card for card in glob_file.cards if card.is_available]
        if(len(available_cards)>=2):
            print("-> Hero has: "+available_cards[0].value+ available_cards[0].color+ ", "+available_cards[1].value+ available_cards[1].color+ "")
        if(len(available_cards)>=5):
            print("Flop is: "+available_cards[2].value+ available_cards[2].color+", "+available_cards[3].value+ available_cards[3].color+", "+available_cards[4].value+ available_cards[4].color+ "")
        if(len(available_cards)>=6):
            print("Turn is: "+available_cards[5].value+ available_cards[5].color+"")
        if(len(available_cards)==7):
            print("River is: "+available_cards[6].value+ available_cards[6].color+"")
    return

def printPlayersInfo():
    players_playing = []
    for player in glob_file.players:
        if player.is_available:
            players_playing.append(player.id)
    print("-> Currently active players are: "+ str(players_playing).strip('[]'))
    return

def printBetsInfo():
    for bet in glob_file.bet_containers:
        if (bet.corresponding_entity=='POT'):
            print("-> There is "+str(bet.value)+" in the central pot")
        else:
            print("Player "+str(bet.corresponding_entity)+' has contributed '+str(bet.value))

def isHeroAvailable():
    if len(glob_file.cards)<2:
        hero_availability = False
    else:
        if(glob_file.cards[0].is_available and glob_file.cards[1].is_available):
            #set Hero as available
            hero_availability = True
        else: hero_availability = False

    return hero_availability

def screenTable(library='xlib'):
    if (library=='xlib'):
        from Xlib import display, X
        ##Get screenshot of the table##
        width,height = int((1/2)*pyautogui.size().width/constants.NB_DISPLAYS),int((4/4)*pyautogui.size().height)
        dsp = display.Display()
        root = dsp.screen().root
        raw = root.get_image(0, 0, width, height, X.ZPixmap, 0xffffffff)
        table_img = Image.frombytes("RGB", (width, height), raw.data, "raw", "BGRX").convert('RGB')
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
        width,height = int((1/2)*pyautogui.size().width/constants.NB_DISPLAYS),int((3/4)*pyautogui.size().height)
        table_img = table_img.crop((0,0,width,height))
       # print(table_img)
        return table_img

    else:
        print("The library: "+library+" can't be used here")


def takeAction(action, amount):
    if action=='fold':
        glob_file.fold.moveTo(click = glob_file.do_clicks)
    elif action=='call':
        if amount==0:
            glob_file.check.moveTo(click= glob_file.do_clicks)
        else:
            glob_file.call.moveTo(click= glob_file.do_clicks)
    elif action == 'raise':
        if glob_file.bet_value_box.is_available:
            glob_file.bet_value_box.moveTo(click=glob_file.do_clicks)
        #TODO, randomize interval
        pyautogui.typewrite(str(amount), interval=0.15)
        if glob_file.raise_to.is_available:
            glob_file.raise_to.moveTo(click=glob_file.do_clicks)
        elif glob_file.bet.is_available:
            glob_file.bet.moveTo(click=glob_file.do_clicks)
        else:
            print('[Error] Trying to bet but both \'bet\' and \'raise_to\' are unavailable')
            
            