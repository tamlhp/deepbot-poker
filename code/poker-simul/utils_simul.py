#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 13:15:22 2019

@author: cyril
"""
import mkl
mkl.set_num_threads(1)
import sys
sys.path.append('../PyPokerEngine_fork/')
sys.path.append('../poker-simul/')
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
from collections import OrderedDict
from neuroevolution import get_flat_params
    
nb_players_6max = 6

def run_one_game_reg(simul_id , gen_id, lstm_bot, nb_hands = 500, ini_stack = 20000, sb_amount = 50, opponents = 'default', verbose=False, cst_decks=None, nb_sub_matches =10):
    mkl.set_num_threads(1)
    #ini_stack=ini_stack/nb_sub_matches
 
    if opponents == 'default':
        #opp_algos = [ConservativeBot(), CallBot(), ManiacBot(), CandidBot()]    
        #opp_names = ['conservative_bot','call_bot', 'maniac_bot', 'candid_bot']
        opp_algos = [CallBot(), ConservativeBot(), EquityBot(), ManiacBot()]    
        opp_names = ['call_bot','conservative_bot', 'equity_bot','maniac_bot']
    else:
        opp_algos = opponents['opp_algos']
        opp_names = opponents['opp_names']

    earnings = OrderedDict()
    ## for each bot to oppose
    for opp_algo, opp_name in zip(opp_algos, opp_names):
        lstm_bot.opponent = opp_name
        lstm_bot.clear_log()
        
        #first match
        my_game_result_1 = 0
        cst_deck_match=cst_decks.copy()
        lstm_bot.model.reset()
        for i in range(nb_sub_matches):
            #print(len(cst_deck_match))
            config = setup_config(max_round=int(nb_hands/nb_sub_matches)-1, initial_stack=ini_stack, small_blind_amount=sb_amount)
            config.register_player(name=lstm_bot.opponent, algorithm=opp_algo)
            config.register_player(name="lstm_bot", algorithm= lstm_bot)
            game_result_1, _ = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_deck_match)
            ##Fixing issue with missing last SB in certain wins
            if game_result_1['players'][1]['stack'] == 2*ini_stack-sb_amount:
                game_result_1['players'][1]['stack'] = 2*ini_stack
            my_game_result_1 += game_result_1['players'][1]['stack']
        if verbose: 
            print("Stack after first game: "+ str(game_result_1))
        
        #return match
        my_game_result_2 = 0
        cst_deck_match=cst_decks.copy()
        lstm_bot.model.reset()
        for i in range(nb_sub_matches):
            #print(len(cst_deck_match))
            config = setup_config(max_round=int(nb_hands/nb_sub_matches)-1, initial_stack=ini_stack, small_blind_amount=sb_amount)
            config.register_player(name="lstm_bot", algorithm=lstm_bot)
            config.register_player(name=lstm_bot.opponent, algorithm=opp_algo)
            game_result_2, _ = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_deck_match)
            ##Fixing issue with missing last SB in certain wins
            if game_result_2['players'][0]['stack'] == 2*ini_stack-sb_amount:
                game_result_2['players'][0]['stack'] = 2*ini_stack
            my_game_result_2 += game_result_2['players'][0]['stack']
            
        if verbose:  
            print("return game: "+ str(game_result_2['players'][0]['stack']))

        earnings[opp_name] = my_game_result_1 + my_game_result_2 - 2*ini_stack
        

   # print('Done with game of bot number: '+ str(lstm_bot.id))
    
    return earnings



def run_one_game_rebuys(lstm_bot, nb_hands = 500, ini_stack = 3000, sb_amount = 50, opponents = 'default', verbose=False, cst_decks=None):
    mkl.set_num_threads(1)
    #ini_stack=ini_stack/nb_sub_matches
    if opponents == 'default':
        #opp_algos = [ConservativeBot(), CallBot(), ManiacBot(), CandidBot()]    
        #opp_names = ['conservative_bot','call_bot', 'maniac_bot', 'candid_bot']
        opp_algos = [CallBot(), ConservativeBot(), EquityBot(), ManiacBot()]    
        opp_names = ['call_bot','conservative_bot', 'equity_bot','maniac_bot']
    else:
        opp_algos = opponents['opp_algos']
        opp_names = opponents['opp_names']

    earnings = OrderedDict()
    ## for each bot to oppose
    for opp_algo, opp_name in zip(opp_algos, opp_names):
        lstm_bot.opponent = opp_name
        lstm_bot.clear_log()
        
        #first match
        max_round = nb_hands
        my_game_result_1 = 0
        cst_deck_match=cst_decks.copy()
        lstm_bot.model.reset()
        while True:
            #print(len(cst_deck_match))
            config = setup_config(max_round=max_round, initial_stack=ini_stack, small_blind_amount=sb_amount)
            config.register_player(name=lstm_bot.opponent, algorithm=opp_algo)
            config.register_player(name="lstm_bot", algorithm= lstm_bot)
            game_result_1, _ = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_deck_match)
            ##Fixing issue with missing last SB in certain wins
            if game_result_1['players'][1]['stack'] == 2*ini_stack-sb_amount:
                game_result_1['players'][1]['stack'] = 2*ini_stack
            my_game_result_1 += game_result_1['players'][1]['stack'] - ini_stack
            max_round-=(lstm_bot.round_count+1)
            if max_round<=0:
                break
            
        if verbose: 
            print("Stack after first game: "+ str(game_result_1))
        
        #return match
        max_round = nb_hands
        my_game_result_2 = 0
        cst_deck_match=cst_decks.copy()
        lstm_bot.model.reset()
        while True:
            #print(len(cst_deck_match))
            config = setup_config(max_round=max_round, initial_stack=ini_stack, small_blind_amount=sb_amount)
            config.register_player(name="lstm_bot", algorithm=lstm_bot)
            config.register_player(name=lstm_bot.opponent, algorithm=opp_algo)
            game_result_2, _ = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_deck_match)
            ##Fixing issue with missing last SB in certain wins
            if game_result_2['players'][0]['stack'] == 2*ini_stack-sb_amount:
                game_result_2['players'][0]['stack'] = 2*ini_stack
            my_game_result_2 += game_result_2['players'][0]['stack'] - ini_stack
            max_round-=(lstm_bot.round_count+1)
            if max_round<=0:
                break
            
        if verbose:  
            print("return game: "+ str(game_result_2['players'][0]['stack']))

        earnings[opp_name] = my_game_result_1 + my_game_result_2 
        

   # print('Done with game of bot number: '+ str(lstm_bot.id))
    
    return earnings



def run_one_game_6max_single(lstm_bot, nb_hands = 250, ini_stack = 1500, sb_amount = 10, opponents = 'default', verbose=False, cst_decks=None):
    mkl.set_num_threads(1)
    #ini_stack=ini_stack/nb_sub_matches
    ## Number of (6) games played vs each opponent:
    nb_full_games_per_opp = 4
    ##the SnG blind structure
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
    
    if opponents == 'default':
        #opp_algos = [ConservativeBot(), CallBot(), ManiacBot(), CandidBot()]    
        #opp_names = ['conservative_bot','call_bot', 'maniac_bot', 'candid_bot']
        opp_algos = [PStratBot]    
        opp_names = ['pstrat_bot_1']
    else:
        opp_algos = opponents['opp_algos']
        opp_names = opponents['opp_names']

    earnings = OrderedDict()
    ## for each bot to oppose
    for opp_algo, opp_name in zip(opp_algos, opp_names):
        lstm_bot.opponent = opp_name
        lstm_bot.clear_log()
        
        max_round = nb_hands
        lstm_bot.model.reset()
        my_game_results = [] # [[-1,]*nb_players_6max,].copy()*nb_full_games_per_opp
        #config = []#[0,]*nb_players_6max*nb_full_games_per_opp
        for full_game_id in range(nb_full_games_per_opp):
            my_game_results.append([-1,]*nb_players_6max)
            ## for each position the hero can find himself
            for ini_hero_pos in range(nb_players_6max):
                #deck of the match
                cst_deck_match=cst_decks[int(full_game_id*nb_players_6max+ini_hero_pos)].copy()
                opp_id=0
                config = setup_config(max_round=max_round, initial_stack=ini_stack, small_blind_amount=sb_amount)
                for i in range(ini_hero_pos):
                    config.register_player(name=lstm_bot.opponent+str(opp_id), algorithm=opp_algo())
                    opp_id+=1
                config.register_player(name="lstm_bot", algorithm= lstm_bot)
                for i in range(nb_players_6max-ini_hero_pos-1):
                    config.register_player(name=lstm_bot.opponent+str(opp_id), algorithm=opp_algo())
                config.set_blind_structure(blind_structure.copy())
                game_result, last_two_players = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_deck_match)
                if lstm_bot.round_count==max_round:
                    print('Game could not finish in max number of hands')
                    my_game_results[full_game_id][ini_hero_pos] = 0
                else:
                    if "lstm_bot" in last_two_players:
                        my_game_results[full_game_id][ini_hero_pos]=1
                    if game_result['players'][ini_hero_pos]['stack']>0:
                        my_game_results[full_game_id][ini_hero_pos]=3
            print(my_game_results)
       
        earnings[opp_name] =np.average(my_game_results)

    
    return earnings



def gen_decks(simul_id, gen_id, log_dir = './simul_data', nb_hands = 500, nb_cards =52, overwrite = True, nb_decks=1):
    
    #create dir for generation
    gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    if not os.path.exists(gen_dir):
        os.makedirs(gen_dir) 
    ### GENERATE ALL DECKS ####
    cst_decks=[0,]*nb_decks
    for i in range(nb_decks):
        cst_decks[i] = reduce(lambda x1,x2: x1+x2, [random.sample(range(1,nb_cards+1),nb_cards) for i in range(nb_hands)]) #the are 52 cards
        # writing down down the list of cards:
    if nb_decks==1:
        cst_decks = cst_decks[0]
    if overwrite==True or not os.path.exists(gen_dir+'/cst_decks.pkl'):
        with open(gen_dir+'/cst_decks.pkl', 'wb') as f:  
            pickle.dump(cst_decks, f, protocol=2)
    return
        
def gen_rand_bots(simul_id, gen_id, log_dir = './simul_data', overwrite=True, nb_bots=50, network='first'):
    #create dir for generation
    gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    if not os.path.exists(gen_dir):
        os.makedirs(gen_dir) 
    
    if not os.path.exists(gen_dir+'/bots'):
        os.makedirs(gen_dir+'/bots') 
        ### GENERATE ALL BOTS ####
    if overwrite == True or not os.path.exists(gen_dir+'/bots/'+str(1)+'/bot_'+str(1)+'_flat.pkl'):
        full_dict = None
        for bot_id in range(1,nb_bots+1): #there are usually 50 bots
            if not os.path.exists(gen_dir+'/bots/'+str(bot_id)):
                os.makedirs(gen_dir+'/bots/'+str(bot_id)) 
            lstm_bot = LSTMBot(id_= bot_id, full_dict=full_dict, gen_dir = gen_dir, network=network)
            with open(gen_dir+'/bots/'+str(lstm_bot.id)+'/bot_'+str(lstm_bot.id)+'_flat.pkl', 'wb') as f:  
                pickle.dump(get_flat_params(lstm_bot.full_dict), f, protocol=0)
    return

class FakeJob:
    def __init__(self, j):
        self.result = j.result