#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 20:28:35 2019

@author: cyril
"""
from scipy.stats import binom
import numpy as np
import matplotlib.pyplot as plt

#### SIMPLE EXPERIMENTS #####
h = 6050 #number of hands
l = 1/5 #freq of hands played
pl = 3 #average nb of players in hand
roi=1.1
n = h*l #nb of hands involved in
eq = roi*(1/pl) # equity with 10% roi
inv = 100 #investment
R_eq = (pl-1)*inv #return with prob ew
R_op_eq = -inv
E = eq*R_eq + (1-eq)*R_op_eq # = 100  good
print('E is : '+str(E))
std = (eq*(R_eq-E)**2 + (1-eq)*(R_op_eq-E)**2)**0.5
print('std is: '+str(std))

k = int(n/pl) # maximum hands lost to still be positive in total
prob_wrong = binom.cdf(k, n, eq)
print('prob wrong: '+ str(prob_wrong))

##### GENERATE GRAPH #####
plt.figure(figsize=(10,5))
pl_arr = [3] #average nb of players in hand
roi_arr= [1.1,1.15,1.2]

l = 1/5 #freq of hands played
max_hands = 12000
for pl in pl_arr:
    for roi in roi_arr:
        nb_points = int(max_hands*l/pl)+1
        eq = roi*(1/pl) # equity with 10% roi
        h_arr = np.linspace(0,max_hands,nb_points)
        n_arr = h_arr*l #nb of hands involved in
        k_arr = (n_arr/pl) # maximum hands lost to still be positive in total
        prob_wrong_arr = np.zeros(nb_points)
        max_iter = nb_points
        for i, n in enumerate(n_arr):
            prob_wrong_arr[i] = binom.cdf(k_arr[i], n, eq)
            if prob_wrong_arr[i] < 10**-4:
                max_iter = i
                break
        plt.subplot(121)
        plt.plot(h_arr[:max_iter],prob_wrong_arr[:max_iter])
        plt.subplot(122)
        plt.semilogy(h_arr[:max_iter],prob_wrong_arr[:max_iter])
plt.subplot(121)
plt.legend(['pl=3, win=100mBB/H','pl=3, win=150mBB/H','pl=3, win=200mBB/H'])
plt.subplot(122)
plt.legend(['pl=3, win=100mBB/H','pl=3, win=150mBB/H','pl=3, win=200mBB/H'])




plt.figure(figsize=(10,5))
pl_arr = [4,3,2] #average nb of players in hand
roi_arr= [1.15]
l = 1/5 #freq of hands played    
max_hands = 12000
for pl in pl_arr:
    for roi in roi_arr:
        eq = roi*(1/pl) # equity with 10% roi
        nb_points = int(max_hands*l/pl)+1
        h_arr = np.linspace(0,max_hands,nb_points)
        n_arr = h_arr*l #nb of hands involved in
        k_arr = (n_arr/pl) # maximum hands lost to still be positive in total
        prob_wrong_arr = np.zeros(nb_points)
        max_iter = nb_points
        for i, n in enumerate(n_arr):
            prob_wrong_arr[i] = binom.cdf(k_arr[i], n, eq)
            if prob_wrong_arr[i] < 10**-4:
                max_iter = i
                break
        plt.subplot(121)
        plt.plot(h_arr[:max_iter],prob_wrong_arr[:max_iter])
        plt.subplot(122)
        plt.semilogy(h_arr[:max_iter],prob_wrong_arr[:max_iter])
plt.subplot(121)
plt.legend(['pl=4, win=150mBB/H','pl=3, win=150mBB/H','pl=2, win=150mBB/H'])
plt.subplot(122)
plt.legend(['pl=4, win=150mBB/H','pl=3, win=150mBB/H','pl=2, win=150mBB/H'])


"""
## 'elite' players playing 1-8 tables returns
NL2: 30bb/100

NL5: 18bb/100

NL10: 12bb/100

NL25: 10bb/100

NL50: 9bb/100

NL100: 8bb/100
"""