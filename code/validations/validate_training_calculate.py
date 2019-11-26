#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 21:25:46 2019

@author: cyril
"""
import sys
sys.path.append('../redis-server/')
sys.path.append('../poker-simul/')

#from utils_simul import gen_rand_bots, gen_decks, FakeJob, run_one_game_reg, run_one_game_rebuys, run_one_game_6max_single, run_one_game_6max_full
from neuroevolution import select_next_gen_bots, get_best_ANE_earnings, get_full_dict
import pickle
import time
import os

from redis import Redis
from rq import Queue
from neuroevolution import compute_ANE
from bot_LSTMBot import LSTMBot
from u_io import prep_gen_dirs, get_all_gen_flat
import random
import numpy as np
from operator import add
import matplotlib.pyplot as plt
my_dpi = 500
            #######
            
def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_extended = np.hstack(([y[0],]*int(box_pts/2),y,[y[-1],]*int(box_pts/2)))
    y_smooth = np.convolve(y_extended, box, mode='valid')
    return y_smooth

my_network='6max_full'

simul_id = 13 ## simul id
if my_network=='second':
    opponent_tables=['call_bot','conservative_bot','equity_bot','maniac_bot']
    my_normalize=True
    nb_opps=4
    ga_popsize= 60
    nb_gens = 250
elif my_network=='6max_full':
    opponent_tables=['call_bot','conservative_bot','maniac_bot','pstrat_bot']
    my_normalize=True
    nb_opps=4
    ga_popsize= 70
    nb_gens=250
elif my_network=='6max_single':
    opponent_tables=['pstrat_bot_1']
    my_normalize=False
    nb_opps=1
    ga_popsize= 70
    nb_gens=250

if __name__ == '__main__':

    #log dir path
    log_dir = '../../../backed_simuls'
    ###CONSTANTS
    nb_hands = 300
    sb_amount = 10
    ini_stack = 1500
    nb_generations = 250
    #nb_sub_matches=10
    BB=1
    normalize=False
    
    all_avg_earnings=[]
    elite_avg_earnings=[]
    
    for gen_id in range(0, nb_gens):
        all_earnings=[]
         #generation's directory
        gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
        
        ## ELITE EARNINGS
        for i in range(ga_popsize):    
            with open(gen_dir+'/bots/'+str(i+1)+'/earnings.pkl', 'rb') as f:  
                earnings = pickle.load(f)
                all_earnings.append(earnings)
        ANEs = compute_ANE(all_earnings=all_earnings, BB=BB, ga_popsize=ga_popsize, nb_opps=nb_opps, normalize=normalize)
        ord_bot_ids = [el+1 for el in sorted(range(len(ANEs)), key=lambda i:ANEs[i], reverse=True)]

        #SELECTING SURVIVORS
        surv_perc = 0.3
        surv_bot_ids = ord_bot_ids[:int(surv_perc*ga_popsize)]  
     
        surv_ANEs = [ANEs[i-1] for i in surv_bot_ids]
        
        ## SELECTING ELITE BOTS
        elite_bot_ids = [id_ for id_ in surv_bot_ids if (ANEs[id_-1]) > sum(surv_ANEs)/float(len(surv_ANEs))]#[:int(len(surv_bot_ids)/2)]      
        elite_earnings=[all_earnings[id_-1] for id_ in elite_bot_ids]
        #print(list(elite_earnings[0].values()))
        elite_earnings = [list(elite_earnings[i].values()) for i in range(len(elite_earnings))]
        elite_avg_earnings.append(np.average(elite_earnings, axis=0))

        ###AVERAGE EARNINGS
        with open(gen_dir+'/surv_earnings.pkl', 'rb') as f:  
            avg_earnings = pickle.load(f)
            all_avg_earnings.append(avg_earnings)
         
all_avg_earnings=np.array(all_avg_earnings)
for i in range(0, len(opponent_tables)):
    table_avg_earnings = smooth(all_avg_earnings[:,i], 11)
    if my_network=='6max_single':
        plt.plot(range(len(table_avg_earnings)),table_avg_earnings*100, color='pink', alpha=0.8)

elite_avg_earnings=np.array(elite_avg_earnings)
for i in range(0,len(opponent_tables)):
    table_avg_earnings = smooth(elite_avg_earnings[:,i], 11)
    if my_network=='second':
        colors=['orange','purple','lightblue','#cc0000']
        plt.plot(range(len(table_avg_earnings)),table_avg_earnings/1000, color=colors[i], alpha=0.8)
        plt.xlabel('Generation', fontsize='large')
        plt.ylabel('mbb/hand', fontsize='large')
        plt.ylim([-50,200])
        plt.legend(['Caller','Conservative','EquityBot','Maniac'])
        plt.savefig('HU_training_roi.png',dpi=my_dpi)
    elif my_network=='6max_single':
        plt.plot(range(len(table_avg_earnings)),table_avg_earnings*100, color='darkgreen', alpha=0.8)
        plt.xlabel('Generation', fontsize='large')
        plt.ylabel('ROI [%]', fontsize='large')
        plt.legend(['All','Elites'])
        plt.savefig('6max_training_roi.png',dpi=my_dpi)
    elif my_network=='6max_full':
        colors=['orange','purple','#cc0000','darkgreen']
        plt.plot(range(len(table_avg_earnings)),table_avg_earnings*100, color=colors[i], alpha=0.8)
        #plt.xlabel('Generation', fontsize='large)
        #plt.ylabel('ROI [%]', fontsize='large')
        #plt.legend(['Loose-Passive','Tight-Passive','Loose-Agressive','Tight-Agressive'])
        plt.tick_params(axis='x', labelsize=14)
        plt.tick_params(axis='y', labelsize=14)
        plt.xlabel('Generation', fontsize=18)
        plt.ylabel('ROI [%]', fontsize=18)
        plt.legend(['LP','TP','LA','TA'], fontsize=14)
        plt.tight_layout()
        plt.savefig('full_6max_training_roi_poster.png',dpi=my_dpi)
    

    