#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 17:48:34 2019

@author: cyril
"""
from ScreenItem import ScreenItem
import pyautogui
from Box import Box
from NumberContainer import NumberContainer
from Number import Number

import constants


class Button(ScreenItem):
    def __init__(self, id_, image_file, detection_confidence, contains_value = False):
        ScreenItem.__init__(self,id_,image_file,detection_confidence)
        self.contains_value = contains_value
        if(contains_value):
            self.value_container = NumberContainer(id_ = self.id, type = 'BUTTON')
        else:
            self.value_container = None
        self.value = 0


    def childUpdateState(self, table_img):
        if(self.never_spotted and self.is_available):
            self.compCenterPosition()
            self.relevant_box = Box(int(self.box.left-constants.RESEARCH_MARGIN*self.box.width),int(self.box.top-constants.RESEARCH_MARGIN*self.box.height),(1+2*constants.RESEARCH_MARGIN)*self.box.width,(1+2*constants.RESEARCH_MARGIN)*self.box.height)
            print('[Button] : "'+ str(self.id) +'" spotted and available')
        if(self.contains_value):
            self.updateValue(table_img)
        return

    def updateValue(self, table_img):
        self.value_container.numbers = []
        if not(self.is_available): return
        numbers_list = []
        table_img_portion = table_img.crop((self.box.left,self.box.top,self.box.left+self.box.width,self.box.top+self.box.height))
        if(True):
            #Attempt to locate stack
            for i, file in enumerate(range(10)):
                file = str(i)+'.png'
                for j, box in enumerate(pyautogui.locateAll(constants.NUMBERS_BUTTON_PATH+file, table_img_portion, confidence=constants.NUMBERS_BUTTON_DET_CONFIDENCE)):
                    if(box!=None):
                        numbers_list.append(Number(value=i, box=box))
                    else:
                        pass
        else:
            pass
        numbers_list.sort(key=lambda number: number.left)
        #print([number.value for number in numbers_list])

        for number in numbers_list:
            self.value_container.addNumber(number)

        self.value_container.computeValue()
        self.value_container.corresponding_entity = self.id
        self.value = self.value_container.value
        print('[Button] '+ str(self.id)+ ' holds value: '+ str(self.value))

        return
