#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 21:43:42 2019

@author: cyril
"""
from random import randint
import pandas as pd
import numpy as np
import csv

def flatten_list(list):
    return [x for sublist in list for x in sublist]
  

def value_estimator(round_state, strat):
    
    value = randint(1,10)
    return value

def write_declare_action_state(action_id, round_id, valid_actions, hole_card, round_state, csv_file = '../../data/hand-data/test_declare_action.csv'):
    state_row = [{'action_id': action_id, 'round_id': round_id, 'hole_card':hole_card, 'valid_actions':valid_actions, 'round_state':round_state}]
    with open(csv_file,'a') as hand_data_csv:
        f_csv = csv.DictWriter(hand_data_csv, ['action_id', 'round_id','hole_card','valid_actions','round_state'])
        if(action_id==0):
            f_csv.writeheader()
        f_csv.writerows(state_row)
    return


def write_round_result_state(round_id, winners, hand_info, round_state, csv_file = '../../data/hand-data/test_round_results.csv'):
    state_row = [{'round_id': round_id, 'winners':winners, 'hand_info':hand_info, 'round_state':round_state}]
    with open(csv_file,'a') as hand_data_csv:
        f_csv = csv.DictWriter(hand_data_csv, ['round_id','winners','hand_info','round_state'])
        if(round_id==0):
            f_csv.writeheader()
        f_csv.writerows(state_row)
    return


def find_action_id(csv_file = '../../data/hand-data/test_declare_action.csv'):
    try:
        with open(csv_file, 'r') as hand_data_csv:
            next_action_id = int(list(csv.reader(hand_data_csv))[-1][0])+1
    except:
        next_action_id = 0
    return next_action_id
    

def find_round_id(csv_file = '../../data/hand-data/test_round_results.csv'):
    try:
        with open(csv_file, 'r') as hand_data_csv:
            next_round_id = int(list(csv.reader(hand_data_csv))[-1][0])+1
    except:
        next_round_id = 0
    return next_round_id


def prepare_net_inputs(declare_action_csv = '../../data/hand-data/test_declare_action.csv', round_result_csv = '../../data/hand-data/test_round_results.csv'):
    declare_action_struct = ['round_id','hole_card','valid_actions','round_state']
    with open(declare_action_csv, 'r') as hand_data_csv:
        df_action = pd.read_csv(hand_data_csv)
    with open(round_result_csv, 'r') as hand_data_csv:
        df_result = pd.read_csv(hand_data_csv)
    
    
    return

    
"""
valid_actions = [{'action': 'fold', 'amount': 0}, {'action': 'call', 'amount': 100}, {'action': 'raise', 'amount': {'min': 150, 'max': 10000}}]
hole_card = ['SA','SK']
round_state = {'action_histories': 
    {'turn': [{'paid': 0, 'uuid': 'dsitwxjfzukumvtbxangpv', 'action': 'CALL', 'amount': 0}, 
              {'paid': 0, 'uuid': 'kydxboxhgkqcosfunbpkxs', 'action': 'CALL', 'amount': 0}], 
    'preflop': [{'add_amount': 50, 'uuid': 'dsitwxjfzukumvtbxangpv', 'action': 'SMALLBLIND', 'amount': 50}, 
                {'add_amount': 50, 'uuid': 'kydxboxhgkqcosfunbpkxs', 'action': 'BIGBLIND', 'amount': 100}, 
                {'action': 'FOLD', 'uuid': 'xkrwhpjormlqgduzvsivsb'}, 
                {'paid': 100, 'uuid': 'wywinfwqxcrtocydvsszbc', 'action': 'CALL', 'amount': 100}, 
                {'paid': 50, 'uuid': 'dsitwxjfzukumvtbxangpv', 'action': 'CALL', 'amount': 100}, 
                {'paid': 0, 'uuid': 'kydxboxhgkqcosfunbpkxs', 'action': 'CALL', 'amount': 100}], 
    'flop': [{'paid': 0, 'uuid': 'dsitwxjfzukumvtbxangpv', 'action': 'CALL', 'amount': 0}, 
             {'paid': 0, 'uuid': 'kydxboxhgkqcosfunbpkxs', 'action': 'CALL', 'amount': 0}, 
             {'paid': 0, 'uuid': 'wywinfwqxcrtocydvsszbc', 'action': 'CALL', 'amount': 0}]}, 
    'community_card': ['HA', 'H4', 'H2', 'S7'], 'pot': {'main': {'amount': 300}, 'side': []}, 
    'street': 'turn', 'dealer_btn': 0, 'next_player': 0, 'small_blind_amount': 50, 
    'seats': [{'state': 'participating', 'name': 'p1', 'uuid': 'wywinfwqxcrtocydvsszbc', 'stack': 9900}, 
              {'state': 'participating', 'name': 'p2', 'uuid': 'dsitwxjfzukumvtbxangpv', 'stack': 9900}, 
              {'state': 'participating', 'name': 'p3', 'uuid': 'kydxboxhgkqcosfunbpkxs', 'stack': 9900}, 
              {'state': 'folded', 'name': 'p4', 'uuid': 'xkrwhpjormlqgduzvsivsb', 'stack': 10000}], 
    'small_blind_pos': 1, 'big_blind_pos': 2, 'round_count': 1}
"""