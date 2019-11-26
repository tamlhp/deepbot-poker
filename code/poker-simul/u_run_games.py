#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 14:47:23 2019

@author: cyril
"""

import sys
sys.path.append('../PyPokerEngine/')
sys.path.append('../poker-simul/')
sys.path.append('./bots/')
import time
import random
import pickle
import mkl
import numpy as np
from collections import OrderedDict
from u_formatting import get_full_dict
from pypokerengine.api.game import setup_config, start_poker

from bot_CallBot import CallBot
from bot_ConservativeBot import ConservativeBot
from bot_ManiacBot import ManiacBot
from bot_PStratBot import PStratBot
from bot_LSTMBot import LSTMBot
from bot_CandidBot import CandidBot
from bot_EquityBot import EquityBot

def run_generation_games(gen_dir, ga_popsize, my_network, my_timeout, train_env, cst_decks, ini_stack, sb_amount, nb_hands, q):
    mkl.set_num_threads(64)
    # Neural network layer size reference
    ref_full_dict = LSTMBot(network=my_network).full_dict
    #Empty jobs list
    jobs = []
    for bot_id in range(1,ga_popsize+1):
        #Load the bot
        with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:
            lstm_bot_flat = pickle.load(f)
            lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, ref_full_dict = ref_full_dict)
            lstm_bot = LSTMBot(id_=bot_id, network=my_network, full_dict = lstm_bot_dict)
        #Enqueue job to play bot's games
        try:
            jobs.append(q.enqueue(run_games, timeout=my_timeout, kwargs = dict(train_env=train_env, lstm_bot=lstm_bot, cst_decks = cst_decks, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands)))
        except ConnectionError:
            print('Currently not connected to redis server')
            continue

    last_enqueue_time = time.time()
    # Fetch jobs' statusses every second
    while True:
        for i in range(len(jobs)):
            if jobs[i].result is not None and not isinstance(jobs[i], FakeJob):
                jobs[i] = FakeJob(jobs[i])
        all_earnings = [j.result for j in jobs]
        time.sleep(1) #1 second
        # If all jobs are done, break
        if None not in all_earnings:
            break
        # If jobs are not finished after timeout threshold, reenqueue.
        # Helps when connection occasionaly breaks. May also be the sign of an error in u_run_games.py.
        if time.time() - last_enqueue_time > my_timeout:
            print('Reenqueuing unfinished jobs '+ str({sum(x is None for x in all_earnings)}))
            for i in range(len(jobs)):
                if jobs[i].result is None:
                    try:
                        jobs[i].cancel()
                        jobs.append(q.enqueue(run_games, timeout=my_timeout, kwargs = dict(train_env=train_env, lstm_bot=lstm_bot, cst_decks = cst_decks, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands)))
                    except ConnectionError:
                        print('Currently not connected to redis server')
                        continue
            last_enqueue_time = time.time()
            if verbose:
                print("Number of jobs remaining: " + str(sum([all_earnings[i]==None for i in range(len(all_earnings))])))
    return all_earnings


def run_games(train_env, lstm_bot, cst_decks, ini_stack=1500, sb_amount=10, nb_hands=300):
    mkl.set_num_threads(1)
    if train_env == 'hu_cash_mixed':
        run_one_game_rebuys(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks)
    elif train_env=='6max_sng_single':
        run_one_game_6max_single(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks)
    elif train_env=='6max_sng_mixed':
        run_one_game_6max_full(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks)
    elif train_env=='fake':
        earnings = run_one_game_fake()
    else:
        print('[run_games] ERROR: train_env not recognized')
    return earnings

def run_one_game_reg(simul_id , gen_id, lstm_bot, verbose=False, cst_decks=None, nb_sub_matches =10):
    """old"""
    #CONFIGURATION
    nb_hands = 500
    ini_stack = 2000
    sb_amount = 50
    opp_algos = [CallBot(), ConservativeBot(), EquityBot(), ManiacBot()]
    opp_names = ['call_bot','conservative_bot', 'equity_bot','maniac_bot']

    earnings = OrderedDict()
    ## for each bot to oppose
    for opp_algo, opp_name in zip(opp_algos, opp_names):

        #first match
        my_game_result_1 = 0
        cst_deck_match=cst_decks.copy()
        lstm_bot.model.reset()
        for i in range(nb_sub_matches):
            config = setup_config(max_round=int(nb_hands/nb_sub_matches)-1, initial_stack=ini_stack, small_blind_amount=sb_amount)
            config.register_player(name=lstm_bot.opponent, algorithm=opp_algo)
            config.register_player(name="lstm_bot", algorithm= lstm_bot)
            game_result_1 = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_deck_match, return_last_two=False)
            #Hacky fix for missing last SB in some results
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
            config = setup_config(max_round=int(nb_hands/nb_sub_matches)-1, initial_stack=ini_stack, small_blind_amount=sb_amount)
            config.register_player(name="lstm_bot", algorithm=lstm_bot)
            config.register_player(name=lstm_bot.opponent, algorithm=opp_algo)
            game_result_2 = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_deck_match, return_last_two=False)
            ##Fixing issue with missing last SB in certain wins
            if game_result_2['players'][0]['stack'] == 2*ini_stack-sb_amount:
                game_result_2['players'][0]['stack'] = 2*ini_stack
            my_game_result_2 += game_result_2['players'][0]['stack']

        if verbose:
            print("return game: "+ str(game_result_2['players'][0]['stack']))

        earnings[opp_name] = my_game_result_1 + my_game_result_2 - 2*ini_stack

    return earnings



def run_one_game_rebuys(lstm_bot, nb_hands = 500, ini_stack = 3000, sb_amount = 50, opponents = 'default', verbose=False, cst_decks=None):
    if opponents == 'default':
        opp_algos = [CallBot(), ConservativeBot(), EquityBot(), ManiacBot()]
        opp_names = ['call_bot','conservative_bot', 'equity_bot','maniac_bot']
    else:
        opp_algos = opponents['opp_algos']
        opp_names = opponents['opp_names']

    earnings = OrderedDict()
    ## for each bot to oppose
    for opp_algo, opp_name in zip(opp_algos, opp_names):

        #first match
        max_round = nb_hands
        my_game_result_1 = 0
        cst_deck_match=cst_decks.copy()
        lstm_bot.model.reset()
        while True:
            config = setup_config(max_round=max_round, initial_stack=ini_stack, small_blind_amount=sb_amount)
            config.register_player(name=lstm_bot.opponent, algorithm=opp_algo)
            config.register_player(name="lstm_bot", algorithm= lstm_bot)
            game_result_1 = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_deck_match, return_last_two=False)
            #Hacky fix for missing last SB in some results
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
            config = setup_config(max_round=max_round, initial_stack=ini_stack, small_blind_amount=sb_amount)
            config.register_player(name="lstm_bot", algorithm=lstm_bot)
            config.register_player(name=lstm_bot.opponent, algorithm=opp_algo)
            game_result_2 = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_deck_match, return_last_two=False)
            #Hacky fix for missing last SB in some results
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



def run_one_game_6max_single(lstm_bot, nb_hands = 250, ini_stack = 1500, sb_amount = 10, opponents = 'default', verbose=False, cst_decks=None, is_validation = False):
    nb_players_6max = 6
    ## Number of full games (6 reg games) played vs each opponent:
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
        opp_algos = [PStratBot]
        opp_names = ['pstrat_bot_1']
    else:
        opp_algos = opponents['opp_algos']
        opp_names = opponents['opp_names']

    earnings = OrderedDict()
    lstm_ranks = OrderedDict()
    ## for each bot to oppose
    for opp_algo, opp_name in zip(opp_algos, opp_names):

        max_round = nb_hands
        lstm_bot.model.reset()
        my_game_results = []
        my_lstm_ranks = []
        for full_game_id in range(nb_full_games_per_opp):
            my_game_results.append([-1,]*nb_players_6max)
            my_lstm_ranks.append([-1,]*nb_players_6max)
            #for each position the hero can find himself
            for ini_hero_pos in range(nb_players_6max):
                #deck of the match
                cst_deck_match=cst_decks[full_game_id].copy()
                opp_id=0
                config = setup_config(max_round=max_round, initial_stack=ini_stack, small_blind_amount=sb_amount)
                for i in range(ini_hero_pos):
                    config.register_player(name=lstm_bot.opponent+str(opp_id), algorithm=opp_algo())
                    opp_id+=1
                config.register_player(name="lstm_bot", algorithm= lstm_bot)
                for i in range(nb_players_6max-ini_hero_pos-1):
                    config.register_player(name=lstm_bot.opponent+str(opp_id), algorithm=opp_algo())
                config.set_blind_structure(blind_structure.copy())
                if is_validation:
                    game_result, last_two_players, lstm_rank = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_deck_match, return_last_two =True, return_lstm_rank=True)
                else:
                    game_result, last_two_players = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_deck_match, return_last_two =True)

                if is_validation:
                    my_lstm_ranks[full_game_id][ini_hero_pos] = lstm_rank+1
                if lstm_bot.round_count==max_round:
                    print('Game could not finish in max number of hands')
                    my_game_results[full_game_id][ini_hero_pos] = 0
                else:
                    if "lstm_bot" in last_two_players:
                        my_game_results[full_game_id][ini_hero_pos]=1
                    if game_result['players'][ini_hero_pos]['stack']>0:
                        my_game_results[full_game_id][ini_hero_pos]=3
            print(my_game_results)

        if is_validation:
            lstm_ranks[opp_name] = my_lstm_ranks
            earnings[opp_name] = my_game_results
        else:
            earnings[opp_name] =np.average(my_game_results)
    if not(is_validation):
        return earnings
    else:
        return earnings, lstm_ranks

def run_one_game_6max_full(lstm_bot, nb_hands = 250, ini_stack = 1500, sb_amount = 10, opponents = 'default', verbose=False, cst_decks=None, is_validation=False):
    nb_players_6max = 6
    # Number of full games (6 reg games) played vs each opponent:
    nb_full_games_per_opp = 4
    ## The SnG blind structure
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
        opp_tables = [[CallBot, CallBot, CallBot, ConservativeBot, PStratBot],
                      [ConservativeBot, ConservativeBot, ConservativeBot, CallBot, PStratBot],
                      [ManiacBot, ManiacBot, ManiacBot, ConservativeBot, PStratBot],
                      [PStratBot, PStratBot, PStratBot, CallBot, ConservativeBot]]
        opp_names = ['call_bot', 'conservative_bot', 'maniac_bot', 'pstrat_bot']
    else:
        opp_algos = opponents['opp_algos']
        opp_names = opponents['opp_names']

    earnings = OrderedDict()
    lstm_ranks = OrderedDict()
    ## for each bot to oppose
    for table_ind in range(4):
        my_game_results = []
        my_lstm_ranks = []
        for full_game_id in range(nb_full_games_per_opp):
            my_game_results.append([-1,]*nb_players_6max)
            my_lstm_ranks.append([-1,]*nb_players_6max)
            ## for each position the hero can find himself
            time_1=time.time()
            for ini_hero_pos in range(nb_players_6max):
                max_round = nb_hands
                lstm_bot.model.reset()
                #deck of the match
                #cst_deck_match=cst_decks[int(full_game_id*nb_players_6max+ini_hero_pos)].copy()
                cst_deck_match=cst_decks[int(table_ind*len(opp_names)+full_game_id)].copy()
                opp_id=1
                config = setup_config(max_round=max_round, initial_stack=ini_stack, small_blind_amount=sb_amount)
                for i in range(ini_hero_pos):
                    config.register_player(name='p-'+str(opp_id), algorithm=opp_tables[table_ind][i]())
                    opp_id+=1
                config.register_player(name="lstm_bot", algorithm= lstm_bot)
                opp_id+=1
                for i in range(ini_hero_pos,nb_players_6max-1):
                    config.register_player(name='p-'+str(opp_id), algorithm=opp_tables[table_ind][i]())
                    opp_id+=1
                config.set_blind_structure(blind_structure.copy())
                if is_validation:
                    game_result, last_two_players, lstm_rank = start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_deck_match, return_last_two =True, return_lstm_rank=True)
                else:
                    game_result, last_two_players= start_poker(config, verbose=0, cheat = True, cst_deck_ids = cst_deck_match, return_last_two =True)

                if is_validation:
                    my_lstm_ranks[full_game_id][ini_hero_pos] = lstm_rank+1
                if lstm_bot.round_count==max_round:
                    print('Game could not finish in max number of hands')
                    my_game_results[full_game_id][ini_hero_pos] = 0
                else:
                    if "lstm_bot" in last_two_players:
                        my_game_results[full_game_id][ini_hero_pos]=1
                    if game_result['players'][ini_hero_pos]['stack']>0:
                        my_game_results[full_game_id][ini_hero_pos]=3
            time_2=time.time()
            print('Time taken:' +str(time_2-time_1))
            print('game results' +str(my_game_results))

        #earnings[opp_names[table_ind]] =np.average(my_game_results)

        if is_validation:
            lstm_ranks[opp_names[table_ind]] = my_lstm_ranks
            earnings[opp_names[table_ind]] = my_game_results
        else:
            earnings[opp_names[table_ind]] =np.average(my_game_results)
    if not(is_validation):
        return earnings
    else:
        return earnings, lstm_ranks

def run_one_game_fake():
    earnings = OrderedDict()
    nb_full_games_per_opp = 4
    for table_ind in range(4):
        earnings['fake_opp'+str(table_ind)] = random.randint(-1,3)
    return earnings

class FakeJob:
    def __init__(self, j):
        self.result = j.result
