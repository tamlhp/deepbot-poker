#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 2

@author: cyril
"""


class Number:
    def __init__(self, value, box):
        self.value = value
        self.left = box.left
        self.top = self.myround(box.top)

    def myround(self, x, base=5):
        return int(base * round(float(x)/base))
