#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 02:55:46 2019

@author: cyril
"""

import sys
sys.path.append('./PyPokerEngine')
sys.path.append('./bots')
sys.path.append('./main_functions')
from pypokerengine.api.game import setup_config, start_poker
from bot_TestBot import TestBot
from bot_CallBot import CallBot
from bot_PStratBot import PStratBot
from bot_LSTMBot import LSTMBot
from bot_EquityBot import EquityBot
from bot_ManiacBot import ManiacBot
from bot_CandidBot import CandidBot
from bot_ConservativeBot import ConservativeBot
import pickle
from u_generate import gen_decks, gen_rand_bots
from functools import reduce
from u_formatting import get_full_dict
from u_neuroevolution import mutate_bots
import random
import numpy as np


agent_file='../data/trained_agents/6max_full/gen_299/bots/1/bot_1_flat.pkl'
my_network = '6max_full'
opp_tables = [[CallBot, CallBot, CallBot, ConservativeBot, PStratBot],
              [ConservativeBot, ConservativeBot, ConservativeBot, CallBot, PStratBot],
              [ManiacBot, ManiacBot, ManiacBot, ConservativeBot, PStratBot],
              [PStratBot, PStratBot, PStratBot, CallBot, ConservativeBot],
              [PStratBot, PStratBot, PStratBot, PStratBot, PStratBot]]
table_ind=3
max_hands = 300


print('## Starting ##')
ref_full_dict = LSTMBot(network=my_network).full_dict
## LOADING AGENT ##
with open(agent_file, 'rb') as f:
  lstm_flat = pickle.load(f)
  lstm_bot_dict = get_full_dict(all_params = lstm_flat, ref_full_dict = ref_full_dict)
  lstm_bot = LSTMBot(full_dict = lstm_bot_dict, network=my_network)

## PREPARING GAME ##
config = setup_config(max_round=max_hands, initial_stack=1500, small_blind_amount=10)
nb_opps, plays_per_blind = 5, 90
for ind in range(nb_opps):
    config.register_player(name="p-"+str(ind+1), algorithm=opp_tables[table_ind][ind]())
config.register_player(name="lstm_bot", algorithm=lstm_bot)

blind_structure={0*plays_per_blind:{'ante':0, 'small_blind':10},\
                 1*plays_per_blind:{'ante':0, 'small_blind':15},\
                 2*plays_per_blind:{'ante':0, 'small_blind':25},\
                 3*plays_per_blind:{'ante':0, 'small_blind':50},\
                 4*plays_per_blind:{'ante':0, 'small_blind':100},\
                 5*plays_per_blind:{'ante':25, 'small_blind':100},\
                 6*plays_per_blind:{'ante':25, 'small_blind':200},\
                 7*plays_per_blind:{'ante':50, 'small_blind':300},\
                 8*plays_per_blind:{'ante':50, 'small_blind':400},\
                 9*plays_per_blind:{'ante':75, 'small_blind':600},}
config.set_blind_structure(blind_structure)

game_result, _, lstm_rank = start_poker(config, verbose=1, return_last_two = True, return_lstm_rank = True)
print(game_result)
my_game_results=-1
lstm_rank+=1
if lstm_bot.round_count==max_hands:
    print('Game could not finish in max number of hands')
    my_game_results = -1
else:
    if int(lstm_rank) <=2:
        my_game_results=1
        lstm_rank=2
    if game_result['players'][5]['stack']>0:
        lstm_rank = 1
        my_game_results=3
print("rank: "+str(lstm_rank))
print("game_result: "+str(my_game_results))
