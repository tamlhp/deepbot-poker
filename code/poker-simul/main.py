#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 14:30:41 2019

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
from neuroevolution import get_full_dict
import random

nb_cards = 52
nb_hands = 500

###CONSTANTS
nb_bots= 1
simul_id = 0
log_dir = './simul_data'
sb_amount = 50
ini_stack = 2000
nb_generations = 250
bot_id = 1
gen_dir='./simul_data/simul_0/gen_0'

lstm_ref = LSTMBot(None)

print('## Starting ##')
## prepare first gen lstm bots and decks
#gen_rand_bots(simul_id = simul_id, gen_id=0, log_dir=log_dir, nb_bots = nb_bots)
gen_decks(simul_id=0,gen_id=0, log_dir=log_dir,nb_hands = 500)

backed_gen_dir = '../../../backed_simuls/simul_5/gen_15'

#backed_gen_dir= './simul_data/simul_5/gen_1'
with open(backed_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:  
    lstm_bot_flat = pickle.load(f)
    lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
    lstm_bot = LSTMBot(id_=bot_id, gen_dir = None, full_dict = lstm_bot_dict)

#load decks
with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
    cst_decks = pickle.load(f)
    
cst_decks_match = cst_decks.copy()
sum_won=0
for i in range(20):
    config = setup_config(max_round=nb_hands, initial_stack=ini_stack, small_blind_amount=50)
    config.register_player(name="p1", algorithm=ManiacBot())
    config.register_player(name="p2", algorithm=CandidBot())
    game_result = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_decks_match)
    #print(game_result)
    sum_won+=game_result['players'][0]['stack']
print(sum_won-20*ini_stack)

"""
log_dir = './simul_data'
gen_decks(simul_id=0,gen_id=0, log_dir=log_dir,nb_hands = 500)


gen_dir='./simul_data/simul_0/gen_0'

with open(gen_dir+'/cst_cheat_ids.pkl', 'rb') as f:  
    cst_cheat_ids = pickle.load(f)

    
time_1 = time.time()
config = setup_config(max_round=500, initial_stack=200000, small_blind_amount=50)
config.register_player(name="p1", algorithm=CandidBot())
config.register_player(name="p2", algorithm=ManiacBot())
config.register_player(name="p3", algorithm=ConservativeBot())
config.register_player(name="p4", algorithm=CallBot())
config.register_player(name="p5", algorithm=PStratBot())
config.register_player(name="p6", algorithm=LSTMBot())

game_result = start_poker(config, verbose=0, cheat = True,cst_cheat_ids = cst_cheat_ids.copy())
time_2 = time.time()
#print(str(time_2-time_1))
print(game_result)
"""
"""
time1 = time.time()
config = setup_config(max_round=1000, initial_stack=200000, small_blind_amount=10)
config.register_player(name="p1", algorithm=EquityBot())
config.register_player(name="p2", algorithm=CallBot())
game_result = start_poker(config, verbose=0)

time2 = time.time()
print('Took %0.3f ms' % ((time2-time1)*1000.0))
"""
#print(game_result)
