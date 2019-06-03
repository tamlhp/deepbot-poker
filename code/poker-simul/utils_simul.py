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
from utils_io import get_flat_params, get_full_dict
    
def run_one_game(simul_id , gen_id, lstm_bot, log_dir = './simul_data', nb_hands = 500, ini_stack = 20000, sb_amount = 50, opponents = 'default', verbose=False, cst_decks=None):
    #gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    #with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
    #    cst_decks = pickle.load(f)
 
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
            pickle.dump(cst_decks, f)
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
            lstm_bot = LSTMBot(id_= bot_id, full_dict=full_dict, gen_dir = gen_dir)
            with open(gen_dir+'/bots/'+str(lstm_bot.id)+'/bot_'+str(lstm_bot.id)+'.pkl', 'wb') as f:  
                pickle.dump(lstm_bot, f)
    return
    
def compute_ANE(all_earnings, BB, load = False, gen_dir = None, nb_opps = 4):
    if load:
        all_earnings = [0,]*50
        for bot_id in range (1,51):
            with open(gen_dir+'/bots/'+str(bot_id)+'/earnings.pkl', 'rb') as f:  
                all_earnings[bot_id-1] = pickle.load(f)
        
    #print(earnings)
    earnings_arr = np.array([list(earning.values()) for earning in all_earnings])
    n_j = np.max([np.ones(nb_opps)*BB,np.max(earnings_arr,axis=0)], axis=0)
    
    return np.sum(earnings_arr/n_j, axis = 1)/nb_opps
    

def select_next_gen_bots(log_dir, simul_id, gen_id, all_earnings, BB, nb_bots):
    old_gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    #creating new generation directory
    new_gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id+1)
    if not os.path.exists(new_gen_dir):
        os.makedirs(new_gen_dir) 
    if not os.path.exists(new_gen_dir+'/bots'):
        os.makedirs(new_gen_dir+'/bots') 
    
    ANEs = compute_ANE(all_earnings, BB)
    ord_bot_ids = [el+1 for el in sorted(range(len(ANEs)), key=lambda i:ANEs[i], reverse=True)]


    #separating surviving bots
    surv_perc = 0.3
    surv_bot_ids = ord_bot_ids[:int(surv_perc*nb_bots)]  
    surv_bots = []
    for bot_id in surv_bot_ids:
        with open(old_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'.pkl', 'rb') as f:  
            surv_bot = pickle.load(f)
            surv_bots.append(surv_bot)
    
    surv_ANEs = [ANEs[i-1] for i in surv_bot_ids]
    elite_bot_ids = [id_ for id_ in surv_bot_ids if ANEs[id_-1] > sum(surv_ANEs)/float(len(surv_ANEs))]
    
    
    ##Preparing elite bots
    elite_bots = []
    for i, bot_id in enumerate(elite_bot_ids):
        with open(old_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'.pkl', 'rb') as f:  
            el_bot = pickle.load(f)
            el_bot.id = i+1
            el_bot.gen_dir = new_gen_dir
            elite_bots.append(el_bot)

    lstm_bot_temp = LSTMBot()
    repro_bots = reproduce_bots(parent_bots = elite_bots, new_gen_dir = new_gen_dir, m_sizes_ref = lstm_bot_temp)
    next_bot_id = len(elite_bots)+len(repro_bots)
    mut_rate = 0.25 - 0.2*gen_id/nb_bots  ##important values
    mut_strength = 0.5 - 0.1*gen_id/nb_bots
    mutant_bots = mutate_bots(orig_bots = surv_bots, nb_new_bots = nb_bots, ref_bot_id=next_bot_id+1, 
                              new_gen_dir = new_gen_dir, mut_rate=mut_rate , mut_strength=mut_strength ,m_sizes_ref = lstm_bot_temp)
    
    new_gen_bots = elite_bots+repro_bots+mutant_bots
    return new_gen_bots

def reproduce_bots(parent_bots, new_gen_dir, m_sizes_ref):
    repro_bots = []
    new_bot_id = len(parent_bots)+1
    for i in range(len(parent_bots)):
        for j in range(i+1,len(parent_bots)):
            first_parent = get_flat_params(full_dict = parent_bots[i].full_dict)
            second_parent = get_flat_params(full_dict = parent_bots[j].full_dict)
            child_flat_params = [first_parent[i] if i%2==0 else second_parent[i] for i in range(len(first_parent))]
            child_full_dict = get_full_dict(all_params = child_flat_params, m_sizes_ref = m_sizes_ref)
            child_bot = LSTMBot(id_=new_bot_id, gen_dir = new_gen_dir, full_dict=child_full_dict)
            repro_bots.append(child_bot)
            new_bot_id+=1
    return repro_bots[:25] # truncate to leave some spots for mutants

def mutate_bots(orig_bots, nb_new_bots, ref_bot_id, new_gen_dir, mut_rate, mut_strength, m_sizes_ref):
    mutant_bots=[]
    for i, new_bot_id in enumerate(range(ref_bot_id, nb_new_bots+1)):
        orig_bot = get_flat_params(orig_bots[i%len(orig_bots)].full_dict)
        mutant_flat_params = [orig_gene if random.random()>mut_rate else  orig_gene + random.gauss(mu=0, sigma=mut_strength) for orig_gene in orig_bot]
        mutant_full_dict = get_full_dict(all_params = mutant_flat_params, m_sizes_ref = m_sizes_ref)
        mutant_bot = LSTMBot(id_=new_bot_id, gen_dir =new_gen_dir, full_dict=mutant_full_dict)
        mutant_bots.append(mutant_bot)
    return mutant_bots
    
