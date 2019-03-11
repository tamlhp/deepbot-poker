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
from ScreenItem import itemExists

class Card():
    def __init__(self, id_, color, box, table, table_img):
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
        

        
               
    def compCardValue(self):
        value=None
        
        #table_img_portion = screenTablePortion(left=self.box.left, top=self.box.top, width=self.size_ref[0], height=self.size_ref[1])
        table_img_portion = self.table_img.crop((self.box.left, self.box.top, self.box.left+self.size_ref[0], self.box.top+self.size_ref[1]))
        #table_img_portion.show()
        for number in self.possible_numbers:
            #print(str(self.confidence_dict[number]))
            if(itemExists(scan_img = table_img_portion, image_path = 'cards/card_'+number+'.png',grayscale=True, detection_confidence=0.7)):
                #print(number)
                if(value==None):
                    value=number
                    
                else:  #special case for 10 (has 2 numbers)
                    print('Two numbers detected!')
                    print(number) 
                    print(value)
        if (value==None):
            print('No number detected!')
            print(number)
        return value
        
    def compCenterPosition(self):
        center_pos= [self.box.left+self.box.width/2,self.box.top+self.box.height/2]
        return center_pos
        
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


        #card_2 = Card(id_='card_2', image_path= 'card_2',detection_confidence=0.65)
        #card_2.locate(table_img)
        #card_3 = Card(id_='card_3', image_path= 'card_3',detection_confidence=0.65)
        #card_3.locate(table_img)
        #card_4 = Card(id_='card_4', image_path= 'card_4.png',detection_confidence=0.9)
        #card_4.locate(table_img)
        #card_5 = Card(id_='card_5', image_path= 'card_5.png',detection_confidence=0.9)
        #card_5.locate(table_img)
        
        
class HeroCards():
    def __init__(self, card1, card2):
        self.card1 = card1
        self.card2 = card2
        
        self.cards = [{'value':card1.value, 'color':card1.color}, {'value':card2.value,'color':card2.color}]
        print("## Hero has: "+self.cards[0]["value"]+ " of "+self.cards[0]["color"]+ " ##")
        print("## And: "+self.cards[1]["value"]+ " of "+ self.cards[1]["color"] + " ##")
        #print(self.card1.value)
        #print(self.card1.color)
        #print(self.card2.value)
        #print(self.card2.color)
              
              
              
              