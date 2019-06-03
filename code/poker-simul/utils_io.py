#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 13:40:29 2019

@author: cyril
"""

import csv
from collections import OrderedDict as OrderedDict
import torch
import re

def write_declare_action_state(action_id, round_id, valid_actions, hole_card, round_state, strat, action, amount, csv_file = './test_declare_action.csv'):
    state_row = [{'round_id': round_id, 'action_id': action_id, 'hole_card':hole_card, 'valid_actions':valid_actions, 
                  'round_state':round_state, 'strat':strat, 'action':action, 'amount':amount}]
    with open(csv_file,'a') as hand_data_csv:
        f_csv = csv.DictWriter(hand_data_csv, ['round_id','action_id','hole_card','valid_actions','round_state','strat','action','amount'])
        
        if(action_id==0):
            f_csv.writeheader()
        f_csv.writerows(state_row)
    return

def write_round_start_state(round_id, seats, csv_file = './test_round_start.csv'):
    state_row = [{'round_id': round_id, 'seats': seats}]
    with open(csv_file,'a') as hand_data_csv:
        f_csv = csv.DictWriter(hand_data_csv, ['round_id','seats'])
        if(round_id==0):
            f_csv.writeheader()
        f_csv.writerows(state_row)
    return

def write_round_result_state(round_id, winners, hand_info, round_state, csv_file = './test_round_results.csv'):
    state_row = [{'round_id': round_id, 'winners':winners, 'hand_info':hand_info, 'round_state':round_state}]
    with open(csv_file,'a') as hand_data_csv:
        f_csv = csv.DictWriter(hand_data_csv, ['round_id','winners','hand_info','round_state'])
        if(round_id==0):
            f_csv.writeheader()
        f_csv.writerows(state_row)
    return


def find_action_id(csv_file = './test_declare_action.csv'):
    try:
        with open(csv_file, 'r') as hand_data_csv:
            next_action_id = int(list(csv.reader(hand_data_csv))[-1][1])+1
    except:
        next_action_id = 0
    return next_action_id


def find_round_id(csv_file = './test_round_results.csv'):
    try:
        with open(csv_file, 'r') as hand_data_csv:
            next_round_id = int(list(csv.reader(hand_data_csv))[-1][0])+1
    except:
        next_round_id = 0
    return next_round_id

    
def get_sep_dicts(full_dict):
    state_dict = OrderedDict()
    i_opp = {}
    i_gen = {}
    for layer in sorted(full_dict.keys()):
        pattern_opp = re.compile('\w\d$')
        pattern_gen = re.compile('\w\d_\d$')
        if pattern_opp.match(layer):
            i_opp[layer] = full_dict[layer]
        elif pattern_gen.match(layer): 
            i_gen[layer] = full_dict[layer]
        else: 
            state_dict[layer] = full_dict[layer]
    return state_dict, i_opp, i_gen

def get_flat_params(full_dict):
    params = torch.Tensor(0)
    for key in sorted(full_dict.keys()):
        params = torch.cat((params, full_dict[key].view(-1)),0)  
    return params

def get_full_dict(all_params, m_sizes_ref):
    dict_sizes=get_dict_sizes(m_sizes_ref.state_dict,m_sizes_ref.model.i_opp,m_sizes_ref.model.i_gen)
    full_dict = {}
    i_start = 0
    for layer in sorted(dict_sizes.keys()):
        full_dict[layer] = torch.Tensor(all_params[i_start:i_start+dict_sizes[layer]['numel']]).view(dict_sizes[layer]['shape'])
        i_start+=dict_sizes[layer]['numel']
    return full_dict


def get_dict_sizes(state_dict, i_opp, i_gen):
    dict_sizes = {}
    all_dicts = state_dict.copy()
    all_dicts.update(i_opp), all_dicts.update(i_gen)
    for key in sorted(all_dicts.keys()):
        dict_sizes[key] = {}
        dict_sizes[key]['numel'] = all_dicts[key].numel()
        dict_sizes[key]['shape'] = list(all_dicts[key].shape)
    return dict_sizes
