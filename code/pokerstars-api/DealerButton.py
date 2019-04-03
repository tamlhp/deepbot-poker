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
from Box import Box

class DealerButton(ScreenItem):
    def __init__(self, id_, image_file, detection_confidence, table):
        ScreenItem.__init__(self,id_,image_file,detection_confidence)
        self.at_player = -1
        self.nb_players = 6
        self.deg_vect_player = self.getPlayerDegTolerance()
        self.table = table


    def search(self, table_img):
        table_img_portion = table_img.crop((self.table.box.left,self.table.box.top,self.table.box.left+self.table.box.width,self.table.box.top+self.table.box.height))
        try:
            #Attempt to locate button
            box_relative = pyautogui.locate('../../data/images/'+self.image_file, table_img_portion, confidence=self.detection_confidence)
            if(box_relative!=None):
                self.box= Box(box_relative.left+self.table.box.left, box_relative.top+self.table.box.top, box_relative.width, box_relative.height)
                self.is_available=True
                print('ScreenItem : "'+ self.id +'" spotted and available')
                self.compCenterPosition()
                self.hasKnownLocation = True
                self.compPlayerId()

            else:
                self.is_available=False
                self.at_player = -1
        except:
            #print('ScreenItem : "'+ self.id +'" is NOT available')
            self.is_available=False
            self.at_player = -1
            pass


    def update(self, table_img):
        table_img_portion = table_img.crop((self.table.box.left,self.table.box.top,self.table.box.left+self.table.box.width,self.table.box.top+self.table.box.height))
        try:
            #Attempt to locate button
            box_relative = pyautogui.locate('../../data/images/'+self.image_file, table_img_portion, confidence=self.detection_confidence)
            if(box_relative!=None):
                self.box= Box(box_relative.left+self.table.box.left, box_relative.top+self.table.box.top, box_relative.width, box_relative.height)
                if(self.is_available==False):
                    #print("[DealerButton]" +str(self.id)+" became available")
                    pass
                self.is_available=True
                self.compCenterPosition()
                self.compPlayerId()
            else:
                if(self.is_available==True):
                    #print("[DealerButton]" +str(self.id)+" became unavailable")
                    pass
                self.is_available=False
                self.at_player = -1
        except:
            if(self.is_available==True):
                #print("[DealerButton]" +str(self.id)+" became unavailable")
                pass
            self.is_available=False
            self.at_player=-1

        #if (table_size==6):
    def getPlayerDegTolerance(self):
        deg_vect_player = [0,]*self.nb_players
        deg_vect_player = [{'right':315, 'left':250},{'right':250,'left':188},{'right':188,'left':150},
                           {'right':150,'left':70},{'right':70,'left':350},{'right':350,'left':315}]
        return deg_vect_player

    def compPlayerId(self):
        if (not self.is_available):
            #print(self.id+' is not available')
            return
        else:
            vect_dealer = [self.center_pos[0]-self.table.center_pos[0],self.center_pos[1]-self.table.center_pos[1]]
            deg_dealer = angle_between([1,0],vect_dealer)
            if(deg_dealer<=0):
                deg_dealer+=360

            for i in range(self.nb_players):
                if((deg_dealer>self.deg_vect_player[i]['left'] and deg_dealer<=self.deg_vect_player[i]['right'])
                    or ((self.deg_vect_player[i]['left']>self.deg_vect_player[i]['right'])  #special case to complete circle
                    and (deg_dealer>self.deg_vect_player[i]['left'] or deg_dealer<=self.deg_vect_player[i]['right']))):
                    self.at_player = i
                    break

        print('-> Dealer button is at player: '+str(self.at_player)+'')

        return self.at_player

    #def printPosition(self):
     #   super(B, self).foo()
