#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 13:18:13 2019

@author: cyril
"""
from ScreenItem import ScreenItem
from extra_functions import angle_between
import numpy as np
import pyautogui
#from actions import screenTable, screenTablePortion
#from actions import initializeTable, getTableState, screenTable
from extra_functions import screenTablePortion
from extra_functions import itemExists
import os
from Box import Box
import glob_file
import constants


class Card():
    def __init__(self, id_, color, box, table_img):
        #ScreenItem.__init__(self,id_,image_path,detection_confidence)
        self.id = id_
        self.box = box
        self.compCenterPosition()
        self.is_available = True

        self.value_detection_confidence = 0.75
        self.hero_deg = {'right':315, 'left':240}
        self.card_values_path = "../../data/api-images/cards/values/"
        self.size_ref = [80,80]
        self.relevant_box = Box(box.left-constants.CARD_REDET_TOL, box.top-constants.CARD_REDET_TOL, box.width+2*constants.CARD_REDET_TOL, box.height+2*constants.CARD_REDET_TOL)
        #self.redetection_tolerance = 20

        self.color = color
        self.value = self.compCardValue(table_img);
        self.isHeroCard = self.isHeroCard(glob_file.table)



    def update(self, table_img):
        table_img_portion = table_img.crop((self.box.left-constants.CARD_REDET_TOL, self.box.top-constants.CARD_REDET_TOL, self.box.left+self.box.width+constants.CARD_REDET_TOL, self.box.top+self.box.height+constants.CARD_REDET_TOL))
        card_colors = ['heart','diamond','club','spade']


        #print('test')
        #table_img_portion.show()
        for i, card_color in enumerate(card_colors):
            try:
                box_relative = pyautogui.locate('../../data/api-images/cards/card_'+card_color+'.png', table_img_portion, confidence=0.9)

                #print(box)
                if(box_relative!=None):
                    box = Box(box_relative.left+self.box.left-constants.CARD_REDET_TOL,box_relative.top+self.box.top-constants.CARD_REDET_TOL,self.box.width,self.box.height)
                    self.box=box
                    self.color = card_color[0]
                    self.value = self.compCardValue(table_img)
                    self.is_available=True
                    #print('test1')

                    #print("Card with id:" +str(self.id)+ " is "+str(self.value)+str(self.color))
                    break
                else:
                    self.is_available=False
                    self.color = None
                    self.value = None

            except:
                self.is_available=False
                self.color = None
                self.value = None
                pass


    def compCardValue(self, table_img):
        value=None

        table_img_portion = table_img.crop((self.box.left, self.box.top, self.box.left+self.size_ref[0], self.box.top+self.size_ref[1]))

        for file in os.listdir(self.card_values_path):
            number = file.split('.')[0].split('_')[1]
            try:
                #Attempt to locate button
                box = pyautogui.locate(self.card_values_path+file, table_img_portion, confidence=self.value_detection_confidence)
                if(box!=None):
                    if(value==None):
                        value=number
                    else:
                        print('[Warning] Two numbers detected!')
            except:
                pass
        if value == '10':
            value = 'T'
        if (value==None):
            print('[Warning] No number detected!')
        return value

    def isHeroCard(self, table):
        vect_card = [self.center_pos[0]-table.center_pos[0],self.center_pos[1]-table.center_pos[1]]
        deg_card = angle_between([1,0],vect_card)
        if(deg_card<=0):
                deg_card+=360
        if (deg_card>self.hero_deg['left'] and deg_card<=self.hero_deg['right']
            and self.center_pos[1]-2*self.box.height>table.center_pos[1]):
            return True
        else:
            return False

    def setId(self, id_):
        self.id=id_
        return

    def compCenterPosition(self):
        self.center_pos= [self.box.left+self.box.width/2,self.box.top+self.box.height/2]
        return self.center_pos
