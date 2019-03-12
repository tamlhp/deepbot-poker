#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 15:01:39 2019

@author: cyril
"""

from ScreenItem import ScreenItem
from extra_functions import angle_between
import numpy as np
import pyautogui

class DealerButton(ScreenItem):
    def __init__(self, id_, image_path, detection_confidence, table_size=6):
        ScreenItem.__init__(self,id_,image_path,detection_confidence)
        self.at_player = -1
        self.deg_vect_player = self.getPlayerDegTolerance(nb_players=6)
        
    def update(self, table, table_img):
        table_img_portion = table_img.crop((table.box.left,table.box.top,table.box.left+self.box.width,table.box.top+self.box.height))
        try:
            box = pyautogui.locate('../data/images/'+self.image_path, table_img_portion, confidence=self.detection_confidence)
            self.is_available=True
            if(box!=self.box):
                self.box=box
                self.compCenterPosition()
                self.compPlayerId(nb_players=6,table=table)
        except:
            self.is_available=False
            self.at_player=-1
    
    def search(self, table_img):
        
        try:
            #Attempt to locate button
            self.box = pyautogui.locate('../data/images/'+self.image_path, table_img, confidence=self.detection_confidence)
            self.is_available=True
            self.compCenterPosition()
            self.hasKnownLocation = True
            self.compPlayerId()
            print('ScreenItem : "'+ self.id +'" spotted and available')
        except:
            #print('ScreenItem : "'+ self.id +'" is NOT available')
            pass
    
        #if (table_size==6):
    def getPlayerDegTolerance(self, nb_players):
        if(nb_players==6):
            deg_vect_player = [0,]*nb_players
        deg_vect_player = [{'right':315, 'left':250},{'right':250,'left':188},{'right':188,'left':150},
                           {'right':150,'left':70},{'right':70,'left':350},{'right':350,'left':315}]
        return deg_vect_player
        
    def compPlayerId(self, nb_players, table):
        if (not self.is_available):
            #print(self.id+' is not available')
            return
        else:
            vect_dealer = [self.center_pos[0]-table.center_pos[0],self.center_pos[1]-table.center_pos[1]]
            deg_dealer = angle_between([1,0],vect_dealer)
            if(deg_dealer<=0):
                deg_dealer+=360
            
            for i in range(nb_players):
                if((deg_dealer>self.deg_vect_player[i]['left'] and deg_dealer<=self.deg_vect_player[i]['right'])
                    or ((self.deg_vect_player[i]['left']>self.deg_vect_player[i]['right'])  #special case to complete circle
                    and (deg_dealer>self.deg_vect_player[i]['left'] or deg_dealer<=self.deg_vect_player[i]['right']))):
                    self.at_player = i
                    break
        
        print('## Dealer is at player: '+str(self.at_player)+' ##')   
            
        return self.at_player
    
    #def printPosition(self):
     #   super(B, self).foo() 
