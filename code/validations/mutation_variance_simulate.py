#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 16:16:37 2019

@author: cyril
"""

import sys
sys.path.append('../PyPokerEngine_fork')
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
from neuroevolution import get_full_dict, mutate_bots, get_flat_params, crossover_bots
import random
import numpy as np

nb_cards = 52
nb_hands = 5

nb_dif_bots=1000

###CONSTANTS
nb_bots= 1
simul_id = -18
log_dir = './simul_data'
sb_amount = 50
ini_stack = 20000
bot_id = 1
my_network='second'

lstm_ref = LSTMBot(None, network=my_network)


#### CONSISTENCY OF RUNS (FROM LOADING)
print('## Starting ##')
## prepare first gen lstm bots and decks
print('\n FIRST LSTM BOT')
validation_id=0
for gen_id in range(nb_dif_bots):
    max_round = nb_hands
    gen_rand_bots(simul_id = simul_id, gen_id=gen_id, log_dir=log_dir, nb_bots = nb_bots, network=my_network, overwrite=True)
    gen_decks(simul_id=simul_id,gen_id=gen_id, log_dir=log_dir,nb_hands = nb_hands, overwrite=True)
    gen_dir='./simul_data/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    #load decks
    with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
        cst_decks = pickle.load(f)
    with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:  
        lstm_bot_flat = pickle.load(f)
        lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
        lstm_bot = LSTMBot(id_=bot_id, gen_dir = gen_dir, full_dict = lstm_bot_dict, network=my_network, validation_mode = 'mutation_variance', validation_id=validation_id)
    while True:
        config = setup_config(max_round=max_round, initial_stack=3000, small_blind_amount=50)
        config.register_player(name="p1", algorithm=lstm_bot)
        config.register_player(name="p2", algorithm=CallBot())
        game_result = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_decks.copy())

        max_round-=(lstm_bot.round_count+1)
        if max_round<=0:
            break


nb_measures=10
##### MUTATION #######
print('\n MUTANT BOT')
validation_ids=np.arange(1,nb_measures)
mut_rates=np.linspace(0.3,0.05,nb_measures)
mut_strengths=np.linspace(0.5,0.1,nb_measures)

for i in range(nb_measures-1):
    print('At measure number: '+str(i+1))
    validation_id=validation_ids[i]
    mutation_rate=mut_rates[i]
    mutation_strength=mut_strengths[i]
    for gen_id in range(nb_dif_bots):
        max_round = nb_hands
        gen_dir='./simul_data/simul_'+str(simul_id)+'/gen_'+str(gen_id)
        #load decks
        with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
            cst_decks = pickle.load(f)
        with open(gen_dir+'/bots/1/bot_1_flat.pkl', 'rb') as f:
            lstm_bot_flat = pickle.load(f)
        #lsmt_bot_full_dict=get_full_dict(all_params=lstm_bot_flat,m_sizes_ref=lstm_ref)
        mutant_flat = mutate_bots(orig_bots_flat=[lstm_bot_flat], nb_new_bots=1, 
                                                  mut_rate=mutation_rate, mut_strength=mutation_strength)[0]
        mutant_dict = get_full_dict(all_params = mutant_flat, m_sizes_ref = lstm_ref)
        mutant_bot = LSTMBot(id_=bot_id, gen_dir = gen_dir, full_dict = mutant_dict, network=my_network, validation_mode = 'mutation_variance', validation_id=validation_id)
        while True:
            config = setup_config(max_round=max_round, initial_stack=3000, small_blind_amount=50)
            config.register_player(name="p1", algorithm=mutant_bot)
            config.register_player(name="p2", algorithm=CallBot())
            game_result = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_decks.copy())
        #print(game_result)
            max_round-=(mutant_bot.round_count+1)
            if max_round<=0:
                break
            
            
