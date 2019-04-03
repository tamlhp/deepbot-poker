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

class Player(ScreenItem):
    def __init__(self, id_, box, table_img, image_file=None, detection_confidence=0.8):
        ScreenItem.__init__(self,id_, image_file,detection_confidence)
        self.id=id_
        self.box=box
        self.table_img = table_img

        self.hole_cards_image = "../../data/images/hole_cards.png"
        self.hole_cards_detection_confidence = 0.8
        self.hole_cards_offset = [40,90]

        self.isPlaying = self.compIsPlaying(self.table_img)

        self.current_bet = 0
        self.bet_box = None
        self.bet_has_known_location = False
        self.bet_detection_confidence = 0.9
        self.bet_numbers_path = "../../data/images/numbers/bets"

    def update(self, table_img):
        self.compIsPlaying(table_img)
        return

    def compIsPlaying(self, table_img):

        table_img_portion = table_img.crop((self.box.left-self.hole_cards_offset[0],self.box.top-self.hole_cards_offset[1],self.box.left+self.box.width+self.hole_cards_offset[0],self.box.top))
        #if(self.id==2):
            #table_img_portion.show()
        try:
            #Attempt to locate player cards
            box_relative = pyautogui.locate(self.hole_cards_image, table_img_portion, confidence=self.hole_cards_detection_confidence)
            if(box_relative!=None):
                #self.box = Box(box_relative.left+self.box.left-self.hole_cards_offset[0], box_relative.top+self.box.top-self.hole_cards_offset[1],box_relative.width,box_relative.height)
                self.is_playing=True
                #print('[Player] : "'+ str(self.id) +'" is playing')
            else:
                self.is_playing=False
                #print('[Player] : "'+ str(self.id) +'" is folded')
        except:
            self.is_playing=False
            print('[Player] : "'+ str(self.id) +'" is folded')
            pass
        return

    def updateBet(self, table_img):
        self.current_bet = 0
        numbers_list = []
        table_img_portion = table_img.crop((self.box.left-100,self.box.top-100,self.box.left+self.box.width+100,self.box.top+self.box.height+100))
        try:
            #Attempt to locate bet
            for i, file in enumerate(os.listdir(self.bet_numbers_path)):
                for j, box_relative in enumerate(pyautogui.locateAll(self.bet_numbers_path+file, table_img_portion, confidence=self.bet_detection_confidence)):
                    if(box_relative!=None):
                        self.bet_has_known_location = True
                        numbers_list.add(Number(left=box_relative.left+self.box.left-100,value=i))
            numbers_list.sort(key=lambda number: number.left)
            self.current_bet = int(reduce(lambda x,y: x+str(y), numList, ''))
            print(self.current_bet)
        except:
            pass
        return
