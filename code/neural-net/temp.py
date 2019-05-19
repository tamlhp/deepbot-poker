#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 15:33:55 2019

@author: cyril
"""

import torch
print(torch.cuda.is_available())

import tensorflow as tf
sess = tf.Session(config=tf.ConfigProto(log_device_placement=True))
