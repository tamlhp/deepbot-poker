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

        
        
class Card():
    def __init__(self, id_, color, box, table, table_img):
        #ScreenItem.__init__(self,id_,image_path,detection_confidence)
        self.id = id_
        self.box = box
        self.compCenterPosition()
        self.is_available = True
        
        self.value_detection_confidence = 0.75
        self.hero_deg = {'right':315, 'left':250}
        #self.possible_numbers = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        self.card_values_path = "../data/images/cards/values/"
        self.size_ref = [80,80]
        self.table_img = table_img
        self.redetection_tolerance = 20
        
        self.color = color
        self.value = self.compCardValue();
        self.isHeroCard = self.isHeroCard(table)
        
        

    def update(self):
        table_img_portion = self.table_img.crop((self.box.left-self.redetection_tolerance, self.box.top-self.redetection_tolerance, self.box.left++self.box.width+self.redetection_tolerance, self.box.top+self.box.height+self.redetection_tolerance))
        card_colors = ['heart','diamond','club','spade']

        for i, card_color in enumerate(card_colors):
            #try:
                box_relative = pyautogui.locate('../data/images/cards/card_'+card_color+'.png', table_img_portion, confidence=0.9)

                #print(box)
                if(box_relative!=None):
                    box = Box(box_relative.left+self.box.left-self.redetection_tolerance,box_relative.top+self.box.top-self.redetection_tolerance,self.box.width,self.box.height)
                    self.box=box
                    self.color = card_color[0]
                    self.value = self.compCardValue()
                    self.is_available=True
                    
                    #print("Card with id:" +str(self.id)+ " is "+str(self.value)+str(self.color))
                    break
                else:
                    self.is_available=False
                    
            #except:
            #    self.is_available=False
            #    pass
               
    def setId(self, id_):
        self.id=id_
        return
    
    def compCardValue(self):
        value=None
        
        table_img_portion = self.table_img.crop((self.box.left, self.box.top, self.box.left+self.size_ref[0], self.box.top+self.size_ref[1]))
        
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
        if (value==None):
            print('[Warning] No number detected!')
        return value
    
    def compCenterPosition(self):
        self.center_pos= [self.box.left+self.box.width/2,self.box.top+self.box.height/2]
        return self.center_pos
    
        
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
        
        
        
        
class CardHolder(ScreenItem):
    def __init__(self, id_, image_path, color,box,table,table_img, detection_confidence=0.7, table_size=6):
        ScreenItem.__init__(self,id_,image_path,detection_confidence)
        #ScreenItem.__init__(self,id_,image_path,detection_confidence)
        self.id = id_
        self.box = box
        self.center_pos= self.compCenterPosition()
        
        self.hero_deg = {'right':315, 'left':250}
        self.possible_numbers = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        self.confidence_dict= {'2':0.7,'3':0.7,'4':0.7,'5':0.7,'6':0.7,'7':0.7,'8':0.6,'9':0.6,'10':0.6,'J':0.6,'Q':0.6,'K':0.6,'A':0.6}
        self.size_ref = [80,80]
        self.table_img = table_img
        
        self.color = color
        self.value = self.compCardValue();
        self.isHeroCard = self.isHeroCard(table)
        
    def update(self, table, table_img):
        table_img_portion = table_img.crop((table.box.left,table.box.top,table.box.left+self.box.width,table.box.top+self.box.height))
        try:
            box_relative = pyautogui.locate('../data/images/'+self.image_path, table_img_portion, confidence=self.detection_confidence)
            box = Box(box_relative.left+table.box.left,box_relative.top+table.box.top,self.box.width,self.box.height)
            if(box_relative==None):
                self.is_available=None
            
            if(box!=self.box or self.is_available==False):
                self.is_available=True
                self.box=box
                self.compCenterPosition()
                self.compPlayerId(nb_players=6,table=table)
        except:
            self.is_available=False
            self.at_player=-1