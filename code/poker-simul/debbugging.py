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
from neuroevolution import get_full_dict
import random

nb_cards = 52
nb_hands = 1

###CONSTANTS
nb_bots= 1
simul_id = 0
log_dir = './simul_data'
sb_amount = 50
ini_stack = 20000
nb_generations = 250
bot_id = 1
gen_dir='./simul_data/simul_0/gen_0'

lstm_ref = LSTMBot(None)

print('## Starting ##')
## prepare first gen lstm bots and decks
#gen_rand_bots(simul_id = simul_id, gen_id=0, log_dir=log_dir, nb_bots = nb_bots)
#gen_decks(simul_id=0,gen_id=0, log_dir=log_dir,nb_hands = 500)
#load bot
with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:  
    lstm_bot_flat = pickle.load(f)
    lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
    print('lstm bot dict: ' + str(lstm_bot_dict['h0_0'][0][0][:5]))
    lstm_bot = LSTMBot(id_=bot_id, gen_dir = None, full_dict = lstm_bot_dict)

#load decks
with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
    cst_decks = pickle.load(f)
print('deck: ' +str(cst_decks[:5])) 
config = setup_config(max_round=nb_hands, initial_stack=20000, small_blind_amount=50)
config.register_player(name="p1", algorithm=lstm_bot)
config.register_player(name="p2", algorithm=ManiacBot())
game_result = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_decks.copy())
#print(game_result)