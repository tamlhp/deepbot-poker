#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 13:15:22 2019

@author: cyril
"""
import mkl
mkl.set_num_threads(1)
import sys
sys.path.append('../PyPokerEngine_fork')
from pypokerengine.api.game import setup_config, start_poker
from bot_CallBot import CallBot
from bot_ConservativeBot import ConservativeBot
from bot_ManiacBot import ManiacBot
from bot_PStratBot import PStratBot
from bot_LSTMBot import LSTMBot
from bot_CandidBot import CandidBot
from bot_EquityBot import EquityBot
import random
import pickle
import numpy as np
import time
from multiprocessing import Pool
import os
from functools import reduce
    
def run_one_game(simul_id , gen_id, lstm_bot, log_dir = './simul_data', nb_hands = 500, ini_stack = 20000, sb_amount = 50, opponents = 'default', verbose=False, cst_decks=None):
    #gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    #with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
    #    cst_decks = pickle.load(f)
    mkl.set_num_threads(1)
 
    if opponents == 'default':
        opp_algos = [ConservativeBot(), CallBot(), ManiacBot(), CandidBot()]    
        opp_names = ['conservative_bot','call_bot', 'maniac_bot', 'candid_bot']
    else:
        opp_algos = opponents['opp_algos']
        opp_names = opponents['opp_names']

    earnings = {}
    ## for each bot to oppose
    for opp_algo, opp_name in zip(opp_algos, opp_names):
        lstm_bot.opponent = opp_name
        lstm_bot.clear_log()
        
        #first match
        config = setup_config(max_round=nb_hands, initial_stack=ini_stack, small_blind_amount=sb_amount)
        config.register_player(name=lstm_bot.opponent, algorithm=opp_algo)
        config.register_player(name="lstm_bot", algorithm= lstm_bot)
        game_result_1 = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_decks.copy())
        if verbose: 
            print("Stack after first game: "+ str(game_result_1['players'][1]['stack']))
        #earnings[opp_name+'_1'] = game_result['players'][1]['stack']
        
        #return match
        lstm_bot.model.reset()
        config = setup_config(max_round=nb_hands, initial_stack=ini_stack, small_blind_amount=sb_amount)
        config.register_player(name="lstm_bot", algorithm=lstm_bot)
        config.register_player(name=lstm_bot.opponent, algorithm=opp_algo)
        game_result_2 = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_decks.copy())
        if verbose:  
            print("return game: "+ str(game_result_2['players'][0]['stack']))
        #earnings[opp_name+'_2'] = game_result['players'][0]['stack']
        earnings[opp_name] = game_result_1['players'][1]['stack'] + game_result_2['players'][0]['stack'] - 2*ini_stack
        

    print('Done with game of bot number: '+ str(lstm_bot.id))
    
    return earnings
 

def gen_decks(simul_id, gen_id, log_dir = './simul_data', nb_hands = 500, nb_cards =52, overwrite = False):
    #create dir for generation
    gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    if not os.path.exists(gen_dir):
        os.makedirs(gen_dir) 
    ### GENERATE ALL DECKS ####
    cst_decks = reduce(lambda x1,x2: x1+x2, [random.sample(range(1,nb_cards+1),nb_cards) for i in range(nb_hands)]) #the are 52 cards
    # writing down down the list of cards:
    if overwrite==True or not os.path.exists(gen_dir+'/cst_decks.pkl'):
        with open(gen_dir+'/cst_decks.pkl', 'wb') as f:  
            pickle.dump(cst_decks, f, protocol=2)
    return
        
def gen_rand_bots(simul_id, gen_id, log_dir = './simul_data', overwrite=False):
    #create dir for generation
    gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    if not os.path.exists(gen_dir):
        os.makedirs(gen_dir) 
    
    if overwrite == True or not os.path.exists(gen_dir+'/bots'):
        os.makedirs(gen_dir+'/bots') 
        ### GENERATE ALL BOTS ####
        full_dict = None
        for bot_id in range(1,51): #there are 50 bots
            os.makedirs(gen_dir+'/bots/'+str(bot_id)) 
            lstm_bot = LSTMBot(id_= bot_id, full_dict=full_dict, gen_dir = gen_dir)
            with open(gen_dir+'/bots/'+str(lstm_bot.id)+'/bot_'+str(lstm_bot.id)+'_dict.pkl', 'wb') as f:  
                pickle.dump(lstm_bot.full_dict, f)
    return
