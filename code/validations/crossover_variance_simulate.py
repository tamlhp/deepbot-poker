#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 16:16:37 2019

@author: cyril
"""

import sys
sys.path.append('../PyPokerEngine')
sys.path.append('../poker-simul')
from pypokerengine.api.game import setup_config, start_poker
from bot_CallBot import CallBot
from bot_PStratBot import PStratBot
from bot_LSTMBot import LSTMBot
from bot_EquityBot import EquityBot
from bot_DeepBot import DeepBot #aka Master Bot
from bot_ManiacBot import ManiacBot
from bot_CandidBot import CandidBot
from bot_ConservativeBot import ConservativeBot
import time
import pickle
from utils_simul import gen_decks, gen_rand_bots
from functools import reduce
from neuroevolution import get_full_dict, get_flat_params, mutate_bots
import random
import numpy as np
from neuroevolution import get_dict_sizes
import torch
         
            
def crossover_bots_odd(parent_bots_flat, m_sizes_ref, nb_new_bots):
    cross_bots = []
    for i in range(nb_new_bots):
        #random approach, parents are selected randomly
        while(True):
            first_parent_id = random.randint(0,len(parent_bots_flat)-1)
            second_parent_id = random.randint(0,len(parent_bots_flat)-1)
            if(first_parent_id != second_parent_id):
                break
        first_parent = parent_bots_flat[first_parent_id]
        second_parent = parent_bots_flat[second_parent_id]
        
        #taking even and odd weights
        child_flat_params = torch.Tensor([first_parent[k].float() if random.random()<0.5 else second_parent[k].float() for k in range(len(first_parent))])
                      
        cross_bots.append(torch.Tensor(child_flat_params))
    return cross_bots

def crossover_bots_avg(parent_bots_flat, m_sizes_ref, nb_new_bots):
    cross_bots = []
    for i in range(nb_new_bots):
        #random approach, parents are selected randomly
        while(True):
            first_parent_id = random.randint(0,len(parent_bots_flat)-1)
            second_parent_id = random.randint(0,len(parent_bots_flat)-1)
            if(first_parent_id != second_parent_id):
                break
        first_parent = parent_bots_flat[first_parent_id]
        second_parent = parent_bots_flat[second_parent_id]
        
        #take average of weights
        child_flat_params = [(first_parent[k] + second_parent[k])/2 for k in range(len(first_parent))]
                       
        cross_bots.append(torch.Tensor(child_flat_params))
    return cross_bots

def crossover_bots_nosplit(parent_bots_flat, m_sizes_ref, nb_new_bots):
    cross_bots = []
    for i in range(nb_new_bots):
        #random approach, parents are selected randomly
        while(True):
            first_parent_id = random.randint(0,len(parent_bots_flat)-1)
            second_parent_id = random.randint(0,len(parent_bots_flat)-1)
            if(first_parent_id != second_parent_id):
                break
        first_parent = parent_bots_flat[first_parent_id]
        second_parent = parent_bots_flat[second_parent_id]

        
        #taking by layer
        dict_sizes=get_dict_sizes(m_sizes_ref.state_dict,m_sizes_ref.model.i_opp,m_sizes_ref.model.i_gen)
        i_start=0
        child_flat_params = []
        for layer in sorted(dict_sizes.keys()):
            if random.random()<0.5:
                child_flat_params= child_flat_params+list(first_parent[i_start:i_start+dict_sizes[layer]['numel']])
            else:
                child_flat_params = child_flat_params+list(second_parent[i_start:i_start+dict_sizes[layer]['numel']])
            i_start+=dict_sizes[layer]['numel']
        
            
        cross_bots.append(torch.Tensor(child_flat_params))
    return cross_bots

def crossover_bots_reg_200(parent_bots_flat, m_sizes_ref, nb_new_bots):
    cross_bots = []
    for i in range(nb_new_bots):
        #random approach, parents are selected randomly
        while(True):
            first_parent_id = random.randint(0,len(parent_bots_flat)-1)
            second_parent_id = random.randint(0,len(parent_bots_flat)-1)
            if(first_parent_id != second_parent_id):
                break
        first_parent = parent_bots_flat[first_parent_id]
        second_parent = parent_bots_flat[second_parent_id]

        
        #taking by layer
        dict_sizes=get_dict_sizes(m_sizes_ref.state_dict,m_sizes_ref.model.i_opp,m_sizes_ref.model.i_gen)
        i_start=0
        child_flat_params = []
        for layer in sorted(dict_sizes.keys()):
            if layer == 'lin_dec_1.weight':  #special case for very large dense layer
                for i in range(int(dict_sizes[layer]['numel']/200)): # splitting by groups of 500
                    if random.random()<0.5:
                        child_flat_params= child_flat_params+list(first_parent[i_start:i_start+200])
                    else:
                        child_flat_params = child_flat_params+list(second_parent[i_start:i_start+200])                
                    i_start+=200
            else:
                if random.random()<0.5:
                    child_flat_params= child_flat_params+list(first_parent[i_start:i_start+dict_sizes[layer]['numel']])
                else:
                    child_flat_params = child_flat_params+list(second_parent[i_start:i_start+dict_sizes[layer]['numel']])
                i_start+=dict_sizes[layer]['numel']
        
            
        cross_bots.append(torch.Tensor(child_flat_params))
    return cross_bots

def crossover_bots_reg_250(parent_bots_flat, m_sizes_ref, nb_new_bots):
    cross_bots = []
    for i in range(nb_new_bots):
        #random approach, parents are selected randomly
        while(True):
            first_parent_id = random.randint(0,len(parent_bots_flat)-1)
            second_parent_id = random.randint(0,len(parent_bots_flat)-1)
            if(first_parent_id != second_parent_id):
                break
        first_parent = parent_bots_flat[first_parent_id]
        second_parent = parent_bots_flat[second_parent_id]

        
        #taking by layer
        dict_sizes=get_dict_sizes(m_sizes_ref.state_dict,m_sizes_ref.model.i_opp,m_sizes_ref.model.i_gen)
        i_start=0
        child_flat_params = []
        for layer in sorted(dict_sizes.keys()):
            if layer == 'lin_dec_1.weight':  #special case for very large dense layer
                for i in range(int(dict_sizes[layer]['numel']/250)): # splitting by groups of 500
                    if random.random()<0.5:
                        child_flat_params= child_flat_params+list(first_parent[i_start:i_start+250])
                    else:
                        child_flat_params = child_flat_params+list(second_parent[i_start:i_start+250])                
                    i_start+=250
            else:
                if random.random()<0.5:
                    child_flat_params= child_flat_params+list(first_parent[i_start:i_start+dict_sizes[layer]['numel']])
                else:
                    child_flat_params = child_flat_params+list(second_parent[i_start:i_start+dict_sizes[layer]['numel']])
                i_start+=dict_sizes[layer]['numel']
        
            
        cross_bots.append(torch.Tensor(child_flat_params))
    return cross_bots

nb_cards = 52
nb_hands = 5

nb_dif_bots=1000

###CONSTANTS
nb_bots= 2
simul_id = -5
log_dir = './simul_data'
sb_amount = 50
ini_stack = 3000
bot_id = 1
my_network='second'

lstm_ref = LSTMBot(None, network=my_network)


#### CONSISTENCY OF RUNS (FROM LOADING)
print('## Starting ##')
## prepare first gen lstm bots and decks
print('\n LSTM BOT')
bot_ids=[1,2]

for gen_id in range(0):
    gen_rand_bots(simul_id = simul_id, gen_id=gen_id, log_dir=log_dir, nb_bots = nb_bots, network=my_network, overwrite=True)
    gen_decks(simul_id=simul_id,gen_id=gen_id, log_dir=log_dir,nb_hands = nb_hands, overwrite=True)
    gen_dir='./simul_data/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    
    for bot_id in bot_ids:
        with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:  
            lstm_bot_flat = pickle.load(f)
        mutant_flat = mutate_bots(orig_bots_flat=[lstm_bot_flat], nb_new_bots=1, 
                                                  mut_rate=0.175, mut_strength=0.3)[0]
        with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'wb') as f:  
            pickle.dump(mutant_flat, f, protocol=0)
    #backed_gen_dir = '../../../backed_simuls/simul_8/gen_'+str(200+gen_id)
    for bot_id in bot_ids:
        max_round = nb_hands
        #load decks
        with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
            cst_decks = pickle.load(f)
        with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:  
            lstm_bot_flat = pickle.load(f)
            lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
            lstm_bot = LSTMBot(id_=bot_id, gen_dir = gen_dir, full_dict = lstm_bot_dict, network=my_network, validation_mode = 'crossover_variance', validation_id=bot_id-1)
        while True:
            config = setup_config(max_round=max_round, initial_stack=3000, small_blind_amount=50)
            config.register_player(name="p1", algorithm=lstm_bot)
            config.register_player(name="p2", algorithm=CallBot())
            game_result = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_decks.copy())
            max_round-=(lstm_bot.round_count+1)
            if max_round<=0:
                break


##### CROSSOVER #######
print('\n CROSSOVER BOT')
validation_ids=[2,3,4,5,6]


for gen_id in range(nb_dif_bots):
    for i,validation_id in enumerate(validation_ids):
        max_round = nb_hands
        gen_dir='./simul_data/simul_'+str(simul_id)+'/gen_'+str(gen_id)
        #backed_gen_dir = '../../../backed_simuls/simul_8/gen_'+str(200+gen_id)
        #load decks
        with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
            cst_decks = pickle.load(f)
        with open(gen_dir+'/bots/1/bot_1_flat.pkl', 'rb') as f:
            lstm_bot_flat = pickle.load(f)
        with open(gen_dir+'/bots/2/bot_2_flat.pkl', 'rb') as f:
            lstm_bot_flat_2 = pickle.load(f)
        #lsmt_bot_full_dict=get_full_dict(all_params=lstm_bot_flat,m_sizes_ref=lstm_ref)
        if validation_id==2:
            cross_flat = crossover_bots_odd([lstm_bot_flat,lstm_bot_flat_2], m_sizes_ref = lstm_ref, nb_new_bots = 1)[0]
        if validation_id==3:
            cross_flat = crossover_bots_avg([lstm_bot_flat,lstm_bot_flat_2], m_sizes_ref = lstm_ref, nb_new_bots = 1)[0]
        if validation_id==4:
            cross_flat = crossover_bots_nosplit([lstm_bot_flat,lstm_bot_flat_2], m_sizes_ref = lstm_ref, nb_new_bots = 1)[0]
        if validation_id==5:
            cross_flat = crossover_bots_reg_200([lstm_bot_flat,lstm_bot_flat_2], m_sizes_ref = lstm_ref, nb_new_bots = 1)[0]
        if validation_id==6:
            cross_flat = crossover_bots_reg_250([lstm_bot_flat,lstm_bot_flat_2], m_sizes_ref = lstm_ref, nb_new_bots = 1)[0]
       
    
        cross_dict = get_full_dict(all_params = cross_flat, m_sizes_ref = lstm_ref)
        cross_bot = LSTMBot(id_=bot_id, gen_dir = gen_dir, full_dict = cross_dict, network=my_network, validation_mode = 'crossover_variance', validation_id=validation_id)
        while True:
            config = setup_config(max_round=max_round, initial_stack=3000, small_blind_amount=50)
            config.register_player(name="p1", algorithm=cross_bot)
            config.register_player(name="p2", algorithm=CallBot())
            game_result = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_decks.copy())
        #print(game_result)
            max_round-=(cross_bot.round_count+1)
            if max_round<=0:
                break
       
