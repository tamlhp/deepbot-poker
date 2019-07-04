#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 18:23:20 2019

@author: cyril
"""

import sys
sys.path.append('../PyPokerEngine_fork')
sys.path.append('../poker-simul')
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
from neuroevolution import get_full_dict, mutate_bots
import random
import numpy as np

nb_players_6max = 6
nb_cards = 52
nb_hands = 250
my_network = 'second'
lstm_ref = LSTMBot(None,network=my_network)

print('## Starting ##')
bot_id = 1
gen_dir='./simul_data/simul_0/gen_0'
backed_gen_dir = '../../../backed_simuls/simul_13/gen_300'
my_network = '6max_full'
table_ind=0

log_dir = './simul_data'

write_details= True
if my_network =='6max_single' or my_network=='6max_full':
    for i in range(1000):
        print('starting match '+str(i))
        nb_decks = 1
        gen_decks(simul_id=0,gen_id=0, log_dir=log_dir,nb_hands = nb_hands, overwrite=True)
        lstm_ref = LSTMBot(None,network=my_network)
        
        with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
            cst_decks = pickle.load(f)
        with open(backed_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:  
            lstm_bot_flat = pickle.load(f)
            #lstm_bot_flat = mutate_bots(orig_bots_flat=[lstm_bot_flat], nb_new_bots=1, 
            #                                      mut_rate=0.1, mut_strength=0.18)[0]
            lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
            lstm_bot = LSTMBot(id_=bot_id, gen_dir = '.', full_dict = lstm_bot_dict, network=my_network, write_details=write_details)
        
        #chosenBot=ManiacBot

        if my_network =='6max_single':
            opp_tables = [[PStratBot, PStratBot, PStratBot, PStratBot, PStratBot]]
            opp_names = ['pstratbot']
        elif my_network=='6max_full':
            opp_tables = [[CallBot, CallBot, CallBot, ConservativeBot, PStratBot],
              [ConservativeBot, ConservativeBot, ConservativeBot, CallBot, PStratBot],
              [ManiacBot, ManiacBot, ManiacBot, ConservativeBot, PStratBot],
              [PStratBot, PStratBot, PStratBot, CallBot, ConservativeBot]]
            opp_names = ['call_bot', 'conservative_bot', 'maniac_bot', 'pstrat_bot']
        
        ini_hero_pos = i%nb_players_6max
        opp_id=1
        
        config = setup_config(max_round=nb_hands, initial_stack=1500, small_blind_amount=10)
        for k in range(ini_hero_pos):
            config.register_player(name='p-'+str(opp_id), algorithm=opp_tables[table_ind][k]())
            opp_id+=1
        config.register_player(name="lstm_bot", algorithm= lstm_bot)
        opp_id+=1
        for k in range(ini_hero_pos,nb_players_6max-1):
            config.register_player(name='p-'+str(opp_id), algorithm=opp_tables[table_ind][k]())
            opp_id+=1

        
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
        
        game_result, last_two_players, lstm_rank = start_poker(config, verbose=0, cheat = True,cst_deck_ids = cst_decks.copy(), return_last_two =True, return_lstm_rank = True)
        my_game_results=-1
        if lstm_bot.round_count==nb_hands:
            print('Game could not finish in max number of hands')
            my_game_results = -1
        else:
            if "lstm_bot" in last_two_players:
                my_game_results=1
            if game_result['players'][5]['stack']>0:
                my_game_results=3
        print('rank: '+str(lstm_rank))