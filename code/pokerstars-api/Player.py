#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 15:59:12 2019

@author: cyril
"""


import pyautogui
from Box import Box
from Number import Number
from ScreenItem import ScreenItem
from NumberContainer import NumberContainer

import constants
import glob_file

class Player(ScreenItem):
    def __init__(self, id_, image_file_path,detection_confidence, player_box, table_img):
        ScreenItem.__init__(self,id_, image_file_path,detection_confidence)

        self.player_box= player_box

        self.box = self.player_box
        self.compCenterPosition()
        self.is_folded = False
        self.bet_value = 0
        self.stack_value = 0
        self.last_bet_seen=0

        self.stack_container = NumberContainer(id_ = self.id, type = 'STACK')
        #self.current_bet = 0
        #self.bet_box = None

        self.relevant_box = Box(self.player_box.left-constants.PLAYER_CARDS_OFFSET[0],self.player_box.top-constants.PLAYER_CARDS_OFFSET[1],self.player_box.width + 2*constants.PLAYER_CARDS_OFFSET[0],constants.PLAYER_CARDS_OFFSET[1])
        self.update(table_img)


    def childUpdateState(self, table_img):
        #read and update the stack of the user
        self.updateStack(table_img)
        return

    def set_availability(self, availability):
        self.is_available = availability
        return
    """
    def setCorrespondingNumbers(self, type_, value):
        if(type_=='STACK'):
            self.stack_value = value
        elif(type_=='BET'):
            self.bet_value = value
    """

    def updateStack(self, table_img):
        self.stack_container.numbers = []

        numbers_list = []
        table_img_portion = table_img.crop((self.player_box.left,self.player_box.top,self.player_box.left+self.player_box.width,self.player_box.top+self.player_box.height+25))
        try:
            #Attempt to locate stack
            for i, file in enumerate(range(10)):
                file = str(i)+'.png'
                for j, box in enumerate(pyautogui.locateAll(constants.NUMBERS_STACK_PATH+file, table_img_portion, confidence=constants.NUMBERS_STACK_DET_CONFIDENCE)):
                    if(box!=None):
                        numbers_list.append(Number(value=i, box=box))
                    else:
                        pass
        except:
            pass
        numbers_list.sort(key=lambda number: number.left)
        #print([number.value for number in numbers_list])

        for number in numbers_list:
            self.stack_container.addNumber(number)

        try:
            self.stack_container.computeValue()
            self.stack_container.corresponding_entity = self.id
            self.stack_value = self.stack_container.value
        except:
            pass

        #print('[Player] Player '+str(self.id)+' has stack of size: '+str(self.stack_value))

        return
