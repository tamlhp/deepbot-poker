#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 17:48:34 2019

@author: cyril
"""

class Button:
    """A simple example class"""
    def __init__(self, id_, image_path, detection_confidence):
        self.id = id_
        self.image_path = image_path
        self.detection_confidence = detection_confidence
        self.box = None