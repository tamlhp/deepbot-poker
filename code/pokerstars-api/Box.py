#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 18:45:21 2019

@author: cyril
"""

class Box():
    def __init__(self, left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
    def __str__(self):
        return ("Box(left="+str(self.left)+", top="+str(self.top)+", width="+str(self.width)+", height="+str(self.height)+")")