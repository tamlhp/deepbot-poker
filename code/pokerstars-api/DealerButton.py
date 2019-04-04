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

import constants

class DealerButton(ScreenItem):
    def __init__(self, id_, image_file, detection_confidence):
        ScreenItem.__init__(self,id_,image_file,detection_confidence)
        self.at_player = -1
        self.table_center = None


    def childUpdateState(self, table_img = None):
        if self.is_available:
            self.compCenterPosition()
            self.compPlayerId()
        return


    def set_table_center(self, table_center):
        self.table_center = table_center

    def compPlayerId(self):
        if (not self.is_available):
            #print(self.id+' is not available')
            return
        else:
            vect_dealer = [self.center_pos[0]-self.table_center[0],self.center_pos[1]-self.table_center[1]]
            deg_dealer = angle_between([1,0],vect_dealer)
            if(deg_dealer<=0):
                deg_dealer+=360
            for i in range(constants.NB_PLAYERS):
                if((deg_dealer>constants.DEG_PLAYERS[i]['left'] and deg_dealer<=constants.DEG_PLAYERS[i]['right'])
                    or ((constants.DEG_PLAYERS[i]['left']>constants.DEG_PLAYERS[i]['right'])  #special case to complete circle
                    and (deg_dealer>constants.DEG_PLAYERS[i]['left'] or deg_dealer<=constants.DEG_PLAYERS[i]['right']))):
                    self.at_player = i
                    break

        print('-> Dealer button is at player: '+str(self.at_player)+'')

        return

    def findRelevantBox(self):
        vect_dealer = [self.center_pos[0]-self.table_center[0],self.center_pos[1]-self.table_center[1]]
        deg_dealer = angle_between([1,0],vect_dealer)

        return

    #def printPosition(self):
     #   super(B, self).foo()
