#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 13:15:22 2019

@author: cyril
"""
import os
os.environ["OMP_NUM_THREADS"] = "1" # export OMP_NUM_THREADS=4
os.environ["OPENBLAS_NUM_THREADS"] = "1" # export OPENBLAS_NUM_THREADS=4 
os.environ["MKL_NUM_THREADS"] = "1" # export MKL_NUM_THREADS=6
os.environ["VECLIB_MAXIMUM_THREADS"] = "1" # export VECLIB_MAXIMUM_THREADS=4
os.environ["NUMEXPR_NUM_THREADS"] = "1" # export NUMEXPR_NUM_THREADS=6

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

  
    
def run_one_game(simul_id , gen_id, lstm_bot, log_dir = './simul_data', nb_hands = 500, ini_stack = 20000, sb_amount = 50, opponents = 'default', verbose=False, cst_cheat_ids=None):
    #gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    #with open(gen_dir+'/cst_cheat_ids.pkl', 'rb') as f:  
    #    cst_cheat_ids = pickle.load(f)
 
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
        game_result_1 = start_poker(config, verbose=0, cheat = True, cst_cheat_ids = cst_cheat_ids.copy())
        if verbose: 
            print("Stack after first game: "+ str(game_result_1['players'][1]['stack']))
        #earnings[opp_name+'_1'] = game_result['players'][1]['stack']
        
        #return match
        lstm_bot.model.reset()
        config = setup_config(max_round=nb_hands, initial_stack=ini_stack, small_blind_amount=sb_amount)
        config.register_player(name="lstm_bot", algorithm=lstm_bot)
        config.register_player(name=lstm_bot.opponent, algorithm=opp_algo)
        game_result_2 = start_poker(config, verbose=0, cheat = True, cst_cheat_ids = cst_cheat_ids.copy())
        if verbose:
            print("Stack after return game: "+ str(game_result_2['players'][0]['stack']))
        #earnings[opp_name+'_2'] = game_result['players'][0]['stack']
        earnings[opp_name] = game_result_1['players'][1]['stack'] + game_result_2['players'][0]['stack'] - 2*ini_stack
        

    print('Done with game of bot number: '+ str(lstm_bot.id))
    
    return earnings



##multiproc style
def run_all_mp():
    time_1 = time.time()
    pool = Pool(processes=8)              # start 4 worker processes
    
    log_dir = './simul_data'
    simul_id = 0 ## simul id
    gen_id = 0 ## gen id
    gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    nb_bots = 8
    nb_hands = 100
    sb_amount = 50
    ini_stack = 20000
    
    ## prepare first gen lstm bots and hands 
    #gen_rand_bots(simul_id = 0,gen_id=0, log_dir=log_dir)
    #gen_decks(simul_id=0,gen_id=0, log_dir=log_dir)
    ## play matches
    with open(gen_dir+'/cst_cheat_ids.pkl', 'rb') as f:  
        cst_cheat_ids = pickle.load(f)
    for bot_id in range(1,nb_bots+1):
        with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'.pkl', 'rb') as f:  
            lstm_bot = pickle.load(f)
        res = pool.map(run_one_game,(), dict(simul_id = 0, gen_id = 0, lstm_bot=lstm_bot, log_dir = log_dir, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_cheat_ids = cst_cheat_ids))
    pool.close()
    pool.join()
    time_2 = time.time()
    print(res)
    print(time_2-time_1)
    return 1
 

def gen_decks(simul_id, gen_id, log_dir = './simul_data', nb_hands = 500):
    #create dir for generation
    gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    if not os.path.exists(gen_dir):
        os.makedirs(gen_dir) 
    ### GENERATE ALL DECKS ####
    cst_cheat_ids = [random.randint(1,52) for i in range(20*nb_hands)] #the are 52 cards
    # writing down down the list of cards:
    with open(gen_dir+'/cst_cheat_ids.pkl', 'wb') as f:  
        pickle.dump(cst_cheat_ids, f)
        
        
def gen_rand_bots(simul_id, gen_id, log_dir = './simul_data'):
    #create dir for generation
    gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    if not os.path.exists(gen_dir):
        os.makedirs(gen_dir) 
    
    if not os.path.exists(gen_dir+'/bots'):
        os.makedirs(gen_dir+'/bots') 

        
    ### GENERATE ALL BOTS ####
    full_dict = None
    for bot_id in range(1,51): #there are 50 bots
        lstm_bot = LSTMBot(id_= bot_id, full_dict=full_dict, gen_dir = gen_dir)
        with open(gen_dir+'/bots/'+str(lstm_bot.id)+'/bot_'+str(lstm_bot.id)+'.pkl', 'wb') as f:  
            pickle.dump(lstm_bot, f)
    
def compute_ANE(gen_dir, BB, nb_opps = 4):
    earnings = [0,]*50
    for bot_id in range (1,51):
        with open(gen_dir+'/bots/'+str(bot_id)+'/earnings.pkl', 'rb') as f:  
            earnings[bot_id-1] = pickle.load(f)
    
    #print(earnings)
    earnings_arr = np.array([list(earning.values()) for earning in earnings])
    n_j = np.max([np.ones(nb_opps)*BB,np.max(earnings_arr,axis=0)], axis=0)
    
    return np.sum(earnings_arr/n_j, axis = 1)/nb_opps
    

def selection_gen_bots(log_dir, simul_id, gen_id, BB, nb_bots):
    
    ANEs = compute_ANE(gen_dir, BB)
    ord_bot_ids = [el+1 for el in sorted(range(len(ANEs)), key=lambda i:ANEs[i], reverse=True)]

    #surv_bot_ids = ord_bot_ids[:int(surv_perc*nb_bots)]
    
    #prime_perc = 0.15
    surv_perc = 0.3
    #prime_bot_ids = ord_bot_ids[:int(prime_perc*nb_bots)]
    #second_bot_ids = ord_bot_ids[int(prime_perc*nb_bots):int(surv_perc*nb_bots)]
    surv_bot_ids = ord_bot_ids[:int(surv_perc*nb_bots)]
    
    surv_ANEs = [ANEs[i-1] for i in surv_bot_ids]

    print(ANEs)
    print(sum(surv_ANEs)/float(len(surv_ANEs)))
    
    prime_bot_ids = [id_ for id_ in surv_bot_ids if ANEs[id_-1] > sum(surv_ANEs)/float(len(surv_ANEs))]
    second_bot_ids = [id_ for id_ in surv_bot_ids if not(ANEs[id_-1] > sum(surv_ANEs)/float(len(surv_ANEs)))]
    
    
    
    print(surv_bot_ids)
    print(prime_bot_ids)
    
