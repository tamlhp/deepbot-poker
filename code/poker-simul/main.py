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
"""
###CONSTANTS
lstm_bot=LSTMBot(network='second')
sum_=0
for key in lstm_bot.full_dict.keys():
    print(key)
    print(lstm_bot.full_dict[key].view(-1).size())
    sum_+=lstm_bot.full_dict[key].view(-1).size()[0]
print(sum_)
"""


for i in range(1):
    log_dir = './simul_data'
    gen_decks(simul_id=0,gen_id=0, log_dir=log_dir,nb_hands = 500, overwrite=True)


    gen_dir='./simul_data/simul_0/gen_0'
    
    with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
        cst_decks = pickle.load(f)
    lstm_bot = LSTMBot(input_type='pstratstyle', network='6max_single')
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
    
    game_result, last_two_players = start_poker(config, verbose=0, cheat = True,cst_deck_ids = cst_decks.copy(), return_last_two = True)
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
time1 = time.time()
config = setup_config(max_round=1000, initial_stack=200000, small_blind_amount=10)
config.register_player(name="p1", algorithm=EquityBot())
config.register_player(name="p2", algorithm=CallBot())
game_result = start_poker(config, verbose=0)

time2 = time.time()
print('Took %0.3f ms' % ((time2-time1)*1000.0))
"""
#print(game_result)
