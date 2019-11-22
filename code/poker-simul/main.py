#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 14:30:41 2019

@author: cyril
"""
import sys
sys.path.append('../PyPokerEngine')
sys.path.append('bots/')
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
from u_generate import gen_decks, gen_rand_bots
from functools import reduce
from u_formatting import get_full_dict
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
"""
my_network = '6max_full'
bot_id = 1
lstm_ref = LSTMBot(network=my_network)
for i in range(1):
    log_dir = './simul_data'
    gen_decks(simul_id=0,gen_id=0, log_dir=log_dir,nb_hands = 500, overwrite=True)


    gen_dir='./simul_data/simul_0/gen_0'

    with open(gen_dir+'/cst_decks.pkl', 'rb') as f:
        cst_decks = pickle.load(f)
    #backed_gen_dir = '../../../backed_simuls/simul_11/gen_30'
    with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:
        lstm_bot_flat = pickle.load(f)
        lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
        lstm_bot = LSTMBot(id_=bot_id, gen_dir = None, full_dict = lstm_bot_dict, network=my_network)

    chosenBot= CallBot

    config = setup_config(max_round=nb_hands, initial_stack=1500, small_blind_amount=10)
    config.register_player(name="p-1", algorithm=chosenBot())
    config.register_player(name="p-2", algorithm=chosenBot())
    config.register_player(name="p-3", algorithm=chosenBot())
    config.register_player(name="p-4", algorithm=chosenBot())
    config.register_player(name="p-5", algorithm=chosenBot())
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

opp_tables = [[CallBot, CallBot, CallBot, ConservativeBot, PStratBot],
              [ConservativeBot, ConservativeBot, ConservativeBot, CallBot, PStratBot],
              [ManiacBot, ManiacBot, ManiacBot, ConservativeBot, PStratBot],
              [PStratBot, PStratBot, PStratBot, CallBot, ConservativeBot]]
opp_names = ['call_bot', 'conservative_bot', 'maniac_bot', 'pstrat_bot']

from collections import OrderedDict
nb_full_games_per_opp=1
nb_players_6max=6

my_network = '6max_full'
bot_id = 1
lstm_bot = LSTMBot(network=my_network)

log_dir = './simul_data'
gen_dir='./simul_data/simul_0/gen_0'
gen_decks(gen_dir=gen_dir,nb_hands = 500, overwrite=True, nb_games=16)
ini_stack=1500
sb_amount=10


with open(gen_dir+'/cst_decks.pkl', 'rb') as f:
    cst_decks = pickle.load(f)

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

earnings = OrderedDict()
## for each bot to oppose
for table_ind in range(4):
    lstm_bot.clear_log()
    my_game_results = [] # [[-1,]*nb_players_6max,].copy()*nb_full_games_per_opp
    #config = []#[0,]*nb_players_6max*nb_full_games_per_opp
    for full_game_id in range(nb_full_games_per_opp):
        my_game_results.append([-1,]*nb_players_6max)
        ## for each position the hero can find himself
        time_1=time.time()
        for ini_hero_pos in range(nb_players_6max):
            max_round = 250
            lstm_bot.model.reset()
            #deck of the match
            #cst_deck_match=cst_decks[int(full_game_id*nb_players_6max+ini_hero_pos)].copy()
            cst_deck_match=cst_decks[int(table_ind*len(opp_names)+full_game_id)].copy()
            opp_id=1
            config = setup_config(max_round=max_round, initial_stack=ini_stack, small_blind_amount=sb_amount)
            for i in range(ini_hero_pos):
                config.register_player(name=str(opp_tables[table_ind][i]), algorithm=opp_tables[table_ind][i]())
                opp_id+=1
            config.register_player(name="lstm_bot_", algorithm= lstm_bot)
            opp_id+=1
            for i in range(ini_hero_pos,nb_players_6max-1):
                config.register_player(name=str(opp_tables[table_ind][i]), algorithm=opp_tables[table_ind][i]())
                opp_id+=1
            config.set_blind_structure(blind_structure.copy())
            game_result, last_two_players = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_deck_match, return_last_two =True)
            print(last_two_players)
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
