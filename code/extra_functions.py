#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 14:59:03 2019

@author: cyril
"""

import random
import numpy as np

def getRandDistrParams():
    beta_=random.uniform(0.1,5);
    alpha_smart=random.uniform(beta_,5);
    alpha_balanced=random.uniform(0.1,5);
    return beta_, alpha_smart, alpha_balanced



def angle_between(v1, v2):
    return np.degrees(np.math.atan2(np.linalg.det([v2,v1]),np.dot(v2,v1)))
