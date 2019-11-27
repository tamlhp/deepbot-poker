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
import pickle
import argparse
from pypokerengine.api.game import setup_config, start_poker
from u_formatting import get_full_dict
from bot_TestBot import TestBot
from bot_CallBot import CallBot
from bot_PStratBot import PStratBot
from bot_DeepBot import DeepBot
from bot_EquityBot import EquityBot
from bot_ManiacBot import ManiacBot
from bot_CandidBot import CandidBot
from bot_ConservativeBot import ConservativeBot

if __name__ == '__main__':
    """ #### PARSE ARGUMENTS #### """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--agent_file', default = '../data/trained_agents/6max_single/gen_250/bots/1/bot_1_flat.pkl', type=str, help='Path to file of a trained agent (in flat format).')
    parser.add_argument('--network', default = '6max_single', type=str, help='Neural network of the agent. [hu_first, hu_second, 6max_single, 6max_full]')
    parser.add_argument('--table_ind', default = 0, type = int, help='Indice of the table of opponents to play against. For more details open this file')
    parser.add_argument('--max_hands', default=300, type=int, help='Maximum number of hands played in a tournament. If attained, the agent is considered to have lost.')

    args = parser.parse_args()
    agent_file = args.agent_file
    my_network = args.network
    table_ind = args.table_ind
    max_hands = args.max_hands

    ##Possible opponent tables##
    opp_tables = [[PStratBot, PStratBot, PStratBot, PStratBot, PStratBot],
                  [CallBot, CallBot, CallBot, ConservativeBot, PStratBot],
                  [ConservativeBot, ConservativeBot, ConservativeBot, CallBot, PStratBot],
                  [ManiacBot, ManiacBot, ManiacBot, ConservativeBot, PStratBot],
                  [PStratBot, PStratBot, PStratBot, CallBot, ConservativeBot]]

    ref_full_dict = DeepBot(network=my_network).full_dict
    """ #### PREPARE AND PLAY GAME #### """
    print('## Starting ##')
    ## LOADING AGENT ##
    with open(agent_file, 'rb') as f:
      deepbot_flat = pickle.load(f)
      deepbot_dict = get_full_dict(all_params = deepbot_flat, ref_full_dict = ref_full_dict)
      deepbot = DeepBot(full_dict = deepbot_dict, network=my_network)

    ## PREPARING GAME ##
    config = setup_config(max_round=max_hands, initial_stack=1500, small_blind_amount=10)
    nb_opps, plays_per_blind = 5, 90
    for ind in range(nb_opps):
        config.register_player(name="p-"+str(ind+1), algorithm=opp_tables[table_ind][ind]())
    config.register_player(name="deepbot", algorithm=deepbot)

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

    game_result, _, deepbot_rank = start_poker(config, verbose=1, return_last_two = True, return_deepbot_rank = True)
    my_game_results=-1
    deepbot_rank+=1
    if deepbot.round_count==max_hands:
        print('Game could not finish in max number of hands')
        my_game_results = -1
    else:
        if int(deepbot_rank) <=2:
            my_game_results=1
            deepbot_rank=2
        if game_result['players'][5]['stack']>0:
            deepbot_rank = 1
            my_game_results=3
    print("\nFinishing place: "+str(deepbot_rank))
    print("Tokens earned: "+str(my_game_results))
