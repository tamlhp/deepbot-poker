#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 14:19:23 2019

@author: cyril
"""
import pickle
import numpy as np 
from functools import reduce
import matplotlib.pyplot as plt
import math

###CONSTANTS

gen_id=-1
ga_popsize= 1
log_dir = '../../../backed_simuls/'
#log_dir = './simul_data/'
sb_amount = 50
ini_stack = 3000
hands_per_match=1000
my_dpi=100

my_network = '6max_full'
simul_nb=13
gen_nb=250
simul_id = '-'+str(simul_nb)+'_'+str(gen_nb)
if my_network =='second':
    with open(log_dir+'/simul_'+str(simul_id)+'/bot_earnings.pkl', 'rb') as f:  
        all_earnings = pickle.load(f)
    
    avg_earnings = np.average([list(all_earnings[i].values()) for i in range(len(all_earnings))],axis=0)
    print('Average Cash earning '+str(avg_earnings))

if my_network=='6max_single':
    with open(log_dir+'/simul_'+str(simul_id)+'/bot_earnings.pkl', 'rb') as f:  
        all_earnings = pickle.load(f)
    
    match_earnings_pre = [list(np.average(all_earnings[i][0]['pstrat_bot_1'],axis=1)) for i in range(len(all_earnings))]
    match_earnings = reduce(lambda x,y :x+y, match_earnings_pre)
        
        
    avg_match_earning = np.average(match_earnings)
    std_match_earning = np.std(match_earnings)
    
    match_rank_pre = [list(np.average(all_earnings[i][1]['pstrat_bot_1'],axis=1)) for i in range(len(all_earnings))]
    match_ranks =[]
    for four_match_ranks in match_rank_pre:
        match_ranks.extend(four_match_ranks)
    avg_match_rank = np.average(match_ranks)
    
    print('Average Match earning '+str(avg_match_earning))
    print('STD Match earning '+str(std_match_earning))
    print('Average match rank: '+str(avg_match_rank))
    
    ranks_pre_pre = [list(all_earnings[i][1]['pstrat_bot_1']) for i in range(len(all_earnings))]
    ranks_pre = reduce(lambda x,y :x+y, ranks_pre_pre)
    ranks = reduce(lambda x,y :x+y, ranks_pre)
    
    fig, ax = plt.subplots()
    ax.set_ylim([0,1])
    N, bins, patches = ax.hist(ranks, bins=[0.5,1.5,2.5,3.5,4.5,5.5,6.5], facecolor='green', alpha=0.5, density = True, align='mid', rwidth = 0.6)
    patches[0].set_facecolor('g') 
    patches[1].set_facecolor('y')
    for i in range(2, len(patches)):
        patches[i].set_facecolor('red')
    
    
    plt.xlabel('Rank', fontsize='large')
    plt.ylabel('Density [%]',fontsize='large')
    plt.savefig('./ranks_images/ranks_6max_single_'+str(gen_nb)+'.png',dpi=my_dpi)
    
    plt.show() 
    

elif my_network=='6max_full':
    titles=['Loose-Passive','Tight-Passive','Loose-Agressive','Tight-Agressive']
    fig, axes = plt.subplots(nrows=2,ncols=2)
    for k, opponent in enumerate(['call_bot','conservative_bot','maniac_bot','pstrat_bot']):
        with open(log_dir+'/simul_'+str(simul_id)+'/bot_earnings.pkl', 'rb') as f:  
            all_earnings = pickle.load(f)
        
        match_earnings_pre = [list(np.average(all_earnings[i][0][opponent],axis=1)) for i in range(len(all_earnings))]
        match_earnings = reduce(lambda x,y :x+y, match_earnings_pre)
            
            
        avg_match_earning = np.average(match_earnings)
        std_match_earning = np.std(match_earnings)
        
        match_rank_pre = [list(np.average(all_earnings[i][1][opponent],axis=1)) for i in range(len(all_earnings))]
        match_ranks =[]
        for four_match_ranks in match_rank_pre:
            match_ranks.extend(four_match_ranks)
        avg_match_rank = np.average(match_ranks)
        
        print('Average Match earning '+str(avg_match_earning))
        print('STD Match earning '+str(std_match_earning))
        print('Average match rank: '+str(avg_match_rank))
        
        ranks_pre_pre = [list(all_earnings[i][1][opponent]) for i in range(len(all_earnings))]
        ranks_pre = reduce(lambda x,y :x+y, ranks_pre_pre)
        ranks = reduce(lambda x,y :x+y, ranks_pre)
        
        axes[math.floor(k/2)][k%2].set_ylim([0,1])
        N, bins, patches = axes[math.floor(k/2)][k%2].hist(ranks, bins=[0.5,1.5,2.5,3.5,4.5,5.5,6.5], facecolor='green', alpha=0.5, density = True, align='mid', rwidth = 0.6)
        patches[0].set_facecolor('g') 
        patches[1].set_facecolor('y')
        for i in range(2, len(patches)):
            patches[i].set_facecolor('red')
        
        axes[math.floor(k/2)][k%2].set_title(titles[k], fontweight='black')
        if math.floor(k/2)==0:
            axes[math.floor(k/2)][k%2].set_xlabel('')
            axes[math.floor(k/2)][k%2].set_xticks([])
        else:
            axes[math.floor(k/2)][k%2].set_xlabel('Rank', fontsize='large')
            axes[math.floor(k/2)][k%2].set_xticks([1,2,3,4,5,6])
    
        if k%2 ==0:
            axes[math.floor(k/2)][k%2].set_ylabel('Density [%]',fontsize='large')
            axes[math.floor(k/2)][k%2].set_yticks([0.00,0.25,0.50,0.75,1.00])
        else:
            axes[math.floor(k/2)][k%2].set_ylabel('')
            axes[math.floor(k/2)][k%2].set_yticks([])
        
    fig.savefig('./ranks_images/ranks_6max_full_'+str(gen_nb)+'.png',dpi=my_dpi)
        
    plt.show() 
           
        
