#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 02:55:46 2019

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
from utils_simul import gen_decks, gen_rand_bots, run_one_game_rebuys
from functools import reduce
from neuroevolution import get_full_dict
import random

nb_cards = 52
nb_hands = 5

###CONSTANTS
nb_bots= 1
simul_id = 0
log_dir = './simul_data'
sb_amount = 50
ini_stack = 3000
nb_generations = 250


my_network = 'second'
lstm_ref = LSTMBot(None,network=my_network)

print('## Starting ##')
"""

bot_id = 1
gen_dir='./simul_data/simul_0/gen_0'

backed_gen_dir = '../../../backed_simuls/simul_8/gen_250'
with open(backed_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:  
    lstm_bot_flat = pickle.load(f)
    lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
    lstm_bot = LSTMBot(id_=bot_id, gen_dir = None, full_dict = lstm_bot_dict, network=my_network)
    
gen_decks(simul_id=simul_id,gen_id=0, log_dir=log_dir,nb_hands = nb_hands)
with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
    cst_decks = pickle.load(f)
cst_decks_match = cst_decks.copy()

earnings = run_one_game_rebuys(lstm_bot=lstm_bot, nb_hands = 500, ini_stack = 3000, sb_amount = 50, opponents = 'default', verbose=False, cst_decks=cst_decks)
#simul_id = -1 , gen_id = -1, log_dir = './simul_data', 
print(earnings)
"""


bot_id = 1
gen_dir='./simul_data/simul_0/gen_0'
backed_gen_dir = '../../../backed_simuls/simul_8/gen_20'

## prepare first gen lstm bots and decks
#gen_rand_bots(simul_id = simul_id, gen_id=0, log_dir=log_dir, nb_bots = nb_bots)
#gen_decks(simul_id=0,gen_id=0, log_dir=log_dir,nb_hands = 500)



#backed_gen_dir= './simul_data/simul_5/gen_1'
with open(backed_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:  
    lstm_bot_flat = pickle.load(f)
    lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
    lstm_bot = LSTMBot(id_=bot_id, gen_dir = None, full_dict = lstm_bot_dict, network=my_network)

#load decks
with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
    cst_decks = pickle.load(f)



#first match
max_round = nb_hands
my_game_result_1 = 0
cst_deck_match=cst_decks.copy()
lstm_bot.model.reset()
while True:
    #print(len(cst_deck_match))
    config = setup_config(max_round=max_round, initial_stack=ini_stack, small_blind_amount=sb_amount)
    config.register_player(name='callbot', algorithm=CallBot())
    config.register_player(name="lstm_bot", algorithm= lstm_bot)
    game_result_1 = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_deck_match)
    ##Fixing issue with missing last SB in certain wins
    if game_result_1['players'][1]['stack'] == 2*ini_stack-sb_amount:
        game_result_1['players'][1]['stack'] = 2*ini_stack
    my_game_result_1 += game_result_1['players'][1]['stack'] - ini_stack
    max_round-=(lstm_bot.round_count+1)
    if max_round<=0:
        break
print(my_game_result_1)

"""
bot_id = 1
gen_dir='./simul_data/simul_0/gen_0'
backed_gen_dir = '../../../backed_simuls/simul_9/gen_290'
my_network = '6max_single'
my_input_type = 'pstratstyle'

log_dir = './simul_data'
gen_decks(simul_id=0,gen_id=0, log_dir=log_dir,nb_hands = 500, overwrite=True)
lstm_ref = LSTMBot(None,network=my_network)

with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
    cst_decks = pickle.load(f)
with open(backed_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:  
    lstm_bot_flat = pickle.load(f)
    lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
    lstm_bot = LSTMBot(id_=bot_id, gen_dir = None, full_dict = lstm_bot_dict, network=my_network, input_type=my_input_type)



config = setup_config(max_round=nb_hands, initial_stack=1500, small_blind_amount=10)
config.register_player(name="p1", algorithm=PStratBot())
config.register_player(name="p2", algorithm=PStratBot())
config.register_player(name="p3", algorithm=PStratBot())
config.register_player(name="p4", algorithm=PStratBot())
config.register_player(name="p5", algorithm=PStratBot())
config.register_player(name="lstm_bot", algorithm=lstm_bot)
#config.register_player(name="p6", algorithm=CallBot())

plays_per_blind=90
blind_structure={0*plays_per_blind:{'ante':0, 'small_blind':10},\
                 1*plays_per_blind:{'ante':0, 'small_blind':15},\
                 2*plays_per_blind:{'ante':0, 'small_blind':25},\
                 3*plays_per_blind:{'ante':0, 'small_blind':50},\
                 4*plays_per_blind:{'ante':0, 'small_blind':100},\
                 5*plays_per_blind:{'ante':25, 'small_blind':100},\
                 6*plays_per_blind:{'ante':25, 'small_blind':200},\
                 7*plays_per_blind:{'ante':50, 'small_blind':300},\
                 8*plays_per_blind:{'ante':50, 'small_blind':400},\
                 9*plays_per_blind:{'ante':75, 'small_blind':600},\
        }
config.set_blind_structure(blind_structure)

game_result, last_two_players = start_poker(config, verbose=0, cheat = True,cst_deck_ids = cst_decks.copy())
time_2 = time.time()
#print(str(time_2-time_1))
my_game_results=-1
if lstm_bot.round_count==nb_hands:
    print('Game could not finish in max number of hands')
    my_game_results = 0
else:
    if "lstm_bot" in last_two_players:
        my_game_results=1
    if game_result['players'][5]['stack']>0:
        my_game_results=3
print(my_game_results)
"""