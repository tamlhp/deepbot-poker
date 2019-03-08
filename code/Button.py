#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 17:48:34 2019

@author: cyril
"""
from ScreenItem import ScreenItem

class Button(ScreenItem):
    def __init__(self, id_, image_path, detection_confidence):
        ScreenItem.__init__(self,id_,image_path,detection_confidence)
