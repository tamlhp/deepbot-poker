#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 21:43:42 2019

@author: cyril
"""

def flatten_list(list):
    return [x for sublist in list for x in sublist]