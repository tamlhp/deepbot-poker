#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 17:48:34 2019

@author: cyril
"""
from ScreenItem import ScreenItem
import pyautogui
from Box import Box


class Button(ScreenItem):
    def __init__(self, id_, image_path, detection_confidence):
        ScreenItem.__init__(self,id_,image_path,detection_confidence)
        
    def update(self,table_img):
        #print(self.box)
        table_img_portion = table_img.crop((self.box.left-self.search_margin*self.box.width,self.box.top-self.search_margin*self.box.height,self.box.left+(1+2*self.search_margin)*self.box.width,self.box.top+(1+2*self.search_margin)*self.box.height))
        try:
            box_relative = pyautogui.locate('../data/images/'+self.image_path, table_img_portion, confidence=self.detection_confidence)

            if(not(box_relative==None)):
                if(self.is_available==False):
                    print("[Menu] "+str(self.id)+" became available")
                box = Box(int(box_relative.left + self.box.left-self.search_margin*self.box.width), int(box_relative.top + self.box.top-self.search_margin*self.box.height), int(self.box.width),int(self.box.height))
                self.box=box
                self.is_available=True
                self.compCenterPosition()
            else:
                if(self.is_available==True):
                    print("[Menu] "+str(self.id)+" became unavailable")
                self.is_available=False
        except:
            if(self.is_available==True):
                    print("[Menu] "+str(self.id)+" became unavailable")
            self.is_available=False
