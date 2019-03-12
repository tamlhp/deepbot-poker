#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 17:48:34 2019

@author: cyril
"""
from ScreenItem import ScreenItem
import pyautogui

class Button(ScreenItem):
    def __init__(self, id_, image_path, detection_confidence):
        ScreenItem.__init__(self,id_,image_path,detection_confidence)
    def update(self,table_img):
        table_img_portion = table_img.crop((self.box.left-self.search_margin*self.width,self.box.top-self.search_margin*self.box.height,self.box.left+(1+2*self.search_margin)*self.box.width),self.box.top+(1+2*self.search_margin)*self.box.height)
        try:
            box = pyautogui.locate('../data/images/'+self.image_path, table_img_portion, confidence=self.detection_confidence)
            self.is_available=True
            if(box!=self.box):
                self.box=box
                self.setCenterPosition()
        except:
            self.is_available=False
