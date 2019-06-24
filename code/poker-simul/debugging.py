#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 16:16:37 2019

@author: cyril
"""

import sys
sys.path.append('../PyPokerEngine_fork')
from pypokerengine.api.game import setup_config, start_poker
from bot_TestBot import TestBot
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

nb_cards = 52
nb_hands = 1

###CONSTANTS
nb_bots= 2
simul_id = 0
log_dir = './simul_data'
sb_amount = 50
ini_stack = 20000
nb_generations = 250
bot_id = 1
gen_dir='./simul_data/simul_0/gen_0'
my_network='second'

lstm_ref = LSTMBot(None, network=my_network)

print(len(lstm_ref.full_dict))
print([len(lstm_ref.full_dict[layer].view(-1)) for layer in lstm_ref.full_dict])

#### CONSISTENCY OF RUNS (FROM LOADING)
print('## Starting ##')
## prepare first gen lstm bots and decks
gen_rand_bots(simul_id = simul_id, gen_id=0, log_dir=log_dir, nb_bots = nb_bots, network=my_network, overwrite=True)
gen_decks(simul_id=0,gen_id=0, log_dir=log_dir,nb_hands = 500)
#load decks
with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
    cst_decks = pickle.load(f)
print('deck: ' +str(cst_decks[:5])) 

print('\n FIRST BOT')
#load first bot
with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:  
    lstm_bot_flat = pickle.load(f)
    lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
    print('lstm bot dict: ' + str(lstm_bot_dict['opp_h0_4'][0][0][:5]))
    #print('lstm_bot_dict: ' +str(lstm_bot_dict['lin_dec_1.weight'][0][:5]))
    #print('lstm_bot_dict: ' +str(lstm_bot_dict['lin_dec_1.weight'][8][:5]))
    lstm_bot = LSTMBot(id_=bot_id, gen_dir = None, full_dict = lstm_bot_dict, network=my_network)
config = setup_config(max_round=nb_hands, initial_stack=20000, small_blind_amount=50)
config.register_player(name="p1", algorithm=lstm_bot)
config.register_player(name="p2", algorithm=ManiacBot())
game_result = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_decks.copy())
#print(game_result)

print('\n SECOND BOT')
#loading second parent bot
with open(gen_dir+'/bots/'+str(bot_id+1)+'/bot_'+str(bot_id+1)+'_flat.pkl', 'rb') as f:  
    lstm_bot_flat_2 = pickle.load(f)
    lstm_bot_dict_2 = get_full_dict(all_params = lstm_bot_flat_2, m_sizes_ref = lstm_ref)
    print('lstm bot 2 dict: ' + str(lstm_bot_dict_2['opp_h0_4'][0][0][:5]))
    #print('lstm bot 2 dict: ' +str(lstm_bot_dict_2['lin_dec_1.weight'][0][:5]))
    #print('lstm bot 2 dict: ' +str(lstm_bot_dict_2['lin_dec_1.weight'][8][:5]))
    lstm_bot_2 = LSTMBot(id_=bot_id+1, gen_dir = None, full_dict = lstm_bot_dict_2, network=my_network)
config = setup_config(max_round=nb_hands, initial_stack=20000, small_blind_amount=50)
config.register_player(name="p1", algorithm=lstm_bot_2)
config.register_player(name="p2", algorithm=ManiacBot())
game_result = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_decks.copy())
#print(game_result)


##### MUTATION #######
print('\n MUTANT BOT')
mutant_flat = mutate_bots(orig_bots_flat=[get_flat_params(lstm_bot.full_dict)], nb_new_bots=1, 
                                          mut_rate=0.3, mut_strength=0.45)[0]
mutant_dict = get_full_dict(all_params = mutant_flat, m_sizes_ref = lstm_ref)
print('mutant dict: ' +str(mutant_dict['opp_h0_4'][0][0][:5]))
    
mutant_bot = LSTMBot(id_=5, gen_dir = None, full_dict = mutant_dict, network=my_network)
config = setup_config(max_round=nb_hands, initial_stack=20000, small_blind_amount=50)
config.register_player(name="p1", algorithm=mutant_bot)
config.register_player(name="p2", algorithm=ManiacBot())
game_result = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_decks.copy())
#print(game_result)

###### CROSSOVER ######
print('\n CROSS BOT')
cross_flat = crossover_bots([get_flat_params(lstm_bot.full_dict),get_flat_params(lstm_bot_2.full_dict)], m_sizes_ref = lstm_ref, nb_new_bots = 1)[0]
cross_dict = get_full_dict(all_params = cross_flat, m_sizes_ref = lstm_ref)
print('cross dict: ' +str(cross_dict['opp_h0_4'][0][0][:5]))
#print('cross dict: ' +str(cross_dict['lin_dec_1.weight'][0][:5]))
#print('cross dict: ' +str(cross_dict['lin_dec_1.weight'][8][:5]))


cross_bot = LSTMBot(id_=6, gen_dir = None, full_dict = cross_dict, network=my_network)
config = setup_config(max_round=nb_hands, initial_stack=20000, small_blind_amount=50)
config.register_player(name="p1", algorithm=cross_bot)
config.register_player(name="p2", algorithm=ManiacBot())
game_result = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_decks.copy())
    