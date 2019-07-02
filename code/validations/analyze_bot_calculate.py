#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 18:38:22 2019

@author: cyril
"""


import sys
sys.path.append('../PyPokerEngine_fork')
from pypokerengine.api.game import setup_config, start_poker
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
import pandas as pd 
import torch
from ast import literal_eval
import matplotlib.pyplot as plt

nb_cards = 52
nb_hands = 250
my_network = 'second'
lstm_ref = LSTMBot(None,network=my_network)

print('## Starting ##')
bot_id = 1
gen_dir='./simul_data/simul_0/gen_0'
backed_gen_dir = '../../../backed_simuls/simul_9/gen_250'
my_network = '6max_single'

log_dir = './simul_data'

write_details= True
if my_network =='6max_single':
    csv_file= '.'+'/analysis_data/'+str(1)+'/declare_action_state.csv'
 
    data = pd.read_csv(csv_file, dtype = {'action':str}) #, dtype = {'round_id':int}, 'action_id':int, 'net_input':np.array, 'net_output':int, 'action':str, 'amount':int
    data.net_input = data.net_input.apply(lambda x: x.strip("[]").split(", "))
    
    #add column sb
    data['bb'] = pd.Series([data.net_input[i][11] for i in range(len(data))], index=data.index)
    data['my_stack'] = pd.Series([data.net_input[i][8] for i in range(len(data))], index=data.index)
    data.my_stack = pd.to_numeric(data.my_stack, errors='coerce')
    data['pos'] = pd.Series([data.net_input[i][5] for i in range(len(data))], index=data.index)


    
    freq_raise = sum(data.action=='raise')/len(data)
    freq_call = sum(data.action=='call')/len(data)
    freq_fold = sum(data.action=='fold')/len(data)
    avg_net_output= data.net_output.where(data.net_output>0, 0).mean()
    avg_raise_value = data.where(data.action=='raise').amount.mean()
    avg_raise_per_bb = data.amount.where(data.action=='raise').groupby(by=data.bb).mean()
    avg_raise_per_stack = data.amount.where(data.action=='raise').groupby(by=lambda x : 1000*round(data.my_stack[x]*1500/1000)).mean()
    nb_decision_facing_raise = sum([bool(np.array(data.net_input[i][9])>np.array(data.net_input[i][11])) for i in range(len(data))])
    nb_decision_facing_raise_reraised = sum(np.logical_and([bool(np.array(data.net_input[i][9])>np.array(data.net_input[i][11])) for i in range(len(data))],data.action=='raise'))
    freq_reraise = nb_decision_facing_raise_reraised/nb_decision_facing_raise
    freq_raise_per_pos = data.groupby(by=data.pos).apply(lambda x: sum(x.action=='raise')/len(x))
    freq_raise_per_bb = data.groupby(by=data.bb).apply(lambda x: sum(x.action=='raise')/len(x))
    stack_at_round = data.my_stack.groupby(by=data.round_id).mean()
    
    print('freq raise :' +str(freq_raise))
    print('freq call :' +str(freq_call))
    print('freq fold :' +str(freq_fold))
    print('avg net output :' +str(avg_net_output))
    print('avg raise value :' +str(avg_raise_value))
    #print('avg raise per bb: ' + str(avg_raise_per_bb))
    #print('avg raise per stack: ' +str(avg_raise_per_stack))
    print('reraise freq: '+str(freq_reraise))
    #print('freq raise per pos: ' +str(freq_raise_per_pos))
    print('freq raise per bb: '+str(freq_raise_per_bb))
    
    missing_round = [int(i) for i in list(np.linspace(1,180,180)) if i not in stack_at_round.index]
    round_axis = list(range(data.round_id.max()))
    for i in missing_round:
        round_axis.remove(i)
    
    plt.plot(round_axis, stack_at_round)
    
    
    
    