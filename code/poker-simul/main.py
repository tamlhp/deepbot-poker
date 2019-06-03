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
from utils_simul import gen_decks
from functools import reduce
import random

nb_cards = 52
nb_hands = 6

cst_decks = reduce(lambda x1,x2: x1+x2, [ [3,3] + random.sample(range(1,nb_cards+1),nb_cards-2) for i in range(nb_hands)]) #  

config = setup_config(max_round=nb_hands, initial_stack=20000, small_blind_amount=1000)
config.register_player(name="p1", algorithm=PStratBot())
config.register_player(name="p2", algorithm=CallBot())
config.register_player(name="p3", algorithm=CallBot())
config.register_player(name="p4", algorithm=CallBot())
config.register_player(name="p5", algorithm=CallBot())
config.register_player(name="p6", algorithm=CallBot())
game_result = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_decks.copy())

#print(game_result)

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
