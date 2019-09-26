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
import os
import pickle
from functools import reduce

def write_declare_action_state(round_id, action_id, net_input, net_output, action, amount, csv_file = './test_declare_action.csv'):
    net_input_cust=list(float(net_input[0][0][i]) for i in range(len(net_input[0][0])))
    #print(list(net_input)[0][0])
    state_row = [{'round_id': round_id, 'action_id': action_id, 'net_input':net_input_cust, 'net_output':net_output, 'action':action, 'amount':amount}]
    csv_path = reduce(lambda x,y :x+'/'+y, csv_file.split('/')[:-1])
    if not os.path.exists(csv_path):
        os.makedirs(csv_path)
        with open(csv_file,'a') as hand_data_csv:
            f_csv = csv.DictWriter(hand_data_csv, ['round_id', 'action_id', 'net_input','net_output','action','amount'])
            f_csv.writeheader()
    with open(csv_file,'a') as hand_data_csv:
        f_csv = csv.DictWriter(hand_data_csv, ['round_id', 'action_id', 'net_input','net_output','action','amount'])
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
