#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 18:38:22 2019

@author: cyril
"""


import sys
sys.path.append('../PyPokerEngine_fork')
sys.path.append('../poker-simul')
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

            
def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_extended = np.hstack(([y[0],]*int(box_pts/2),y,[y[-1],]*int(box_pts/2)))
    y_smooth = np.convolve(y_extended, box, mode='valid')
    return y_smooth

print('## Starting ##')
bot_id = 1
my_network = '6max_full'
table_ind=3

my_dpi =200

if my_network=='6max_single':
    data_dir = '/6max_single_1000'
elif my_network=='6max_full':
    data_dir = '/6max_full_'+str(table_ind)+'_1000'

write_details= True
if my_network =='6max_single' or my_network=='6max_full':
    
    if False:
        csv_file= './analysis_data/'+data_dir+'/declare_action_state.csv'
     
        data = pd.read_csv(csv_file, dtype = {'action':str}) #, dtype = {'round_id':int}, 'action_id':int, 'net_input':np.array, 'net_output':int, 'action':str, 'amount':int
        data.net_input = data.net_input.apply(lambda x: x.strip("[]").split(", "))
        
        #add column sb
        data['bb'] = pd.Series([data.net_input[i][11] for i in range(len(data))], index=data.index)
        data.bb = pd.to_numeric(data.bb, errors='coerce')
        data['my_stack'] = pd.Series([data.net_input[i][8] for i in range(len(data))], index=data.index)
        data.my_stack = pd.to_numeric(data.my_stack, errors='coerce')
        data['pos'] = pd.Series([data.net_input[i][5] for i in range(len(data))], index=data.index)
        data.pos = pd.to_numeric(data.pos, errors='coerce')
        data['preflop'] = pd.Series([data.net_input[i][0] for i in range(len(data))], index=data.index)
        data.preflop = pd.to_numeric(data.preflop, errors='coerce')
        data['call_price'] = pd.Series([data.net_input[i][9] for i in range(len(data))], index=data.index)
        data.call_price = pd.to_numeric(data.call_price, errors='coerce')
        data['street'] = [data.net_input[i][:4].index('1.0') for i in range(len(data))]
        data.street = pd.to_numeric(data.street, errors='coerce')
        data['nb_opps'] = pd.Series([data.net_input[i][4] for i in range(len(data))], index=data.index)
        data.nb_opps = pd.to_numeric(data.nb_opps, errors='coerce')
        data['equity'] =pd.Series([data.net_input[i][6] for i in range(len(data))], index=data.index)
        data.equity = pd.to_numeric(data.equity, errors='coerce')
        if my_network=='6max_single':
            data.equity=data.equity*(6*data.nb_opps+1)
            
        freq_raise = sum(data.action=='raise')/len(data)
        freq_call = sum(data.action=='call')/len(data)
        freq_fold = sum(data.action=='fold')/len(data)
        freq_raise_by_round = sum(data.action=='raise')/len(data)
        freq_call_by_round = sum(data.action=='call')/len(data)
        freq_fold_by_round = sum(data.action=='fold')/len(data)        
        avg_net_output= data.net_output.where(data.net_output>0, 0).mean()
        avg_raise_value = data.where(data.action=='raise').amount.mean()
        avg_raise_per_bb = data.amount.where(data.action=='raise').groupby(by=data.bb).mean()
        avg_raise_per_stack = data.amount.where(data.action=='raise').groupby(by=lambda x : 1000*round(data.my_stack[x]*1500/1000)).mean()
        

        stack_at_round = data.my_stack.groupby(by=data.round_id).mean()*1500
        raise_amount_at_round = data.where(data.action=='raise').amount.groupby(by=data.round_id).mean()
    
        freq_raise_round = data.groupby(by=data.round_id).apply(lambda x: sum(x.action=='raise')/len(x))
        freq_check_round = data.groupby(by=data.round_id).apply(lambda x: sum(np.logical_and(x.action=='call', x.amount<1))/len(x))
        freq_call_round = data.groupby(by=data.round_id).apply(lambda x: sum(np.logical_and(x.action=='call', x.amount>1))/len(x))
        freq_fold_round = data.groupby(by=data.round_id).apply(lambda x: sum(x.action=='fold')/len(x))
    
            
        freq_reraise_round = data.groupby(by=6*round(data.round_id/6)).apply(lambda data: sum(np.logical_and(data.action=='raise',np.logical_or(np.logical_and(data.call_price>0, data.preflop==0), np.logical_and(data.call_price>data.bb, data.preflop==1)))) \
                                    /(sum(np.logical_or(np.logical_and(data.call_price>0, data.preflop==0), np.logical_and(data.call_price>data.bb, data.preflop==1)))+1))
    
        freq_openraise_round = data.groupby(by=6*round(data.round_id/6)).apply(lambda data: sum(np.logical_and(data.action=='raise',np.logical_or(np.logical_and(data.call_price==0, data.preflop==0), np.logical_and(data.call_price<=data.bb, data.preflop==1)))) \
                                    /(sum(np.logical_or(np.logical_and(data.call_price==0, data.preflop==0), np.logical_and(data.call_price<=data.bb, data.preflop==1)))+1))
    
        nb_raise_equity = data.groupby(by=round(20*data.equity)/20).apply(lambda x: sum(x.action=='raise'))
        len_equity = data.groupby(by=round(20*data.equity)/20).apply(lambda x: len(x))
        freq_raise_equity=[]
        borders = [0,0.75,1,1.25,6]
        for i in range(len(borders)-1):
            nb_raise_batch=nb_raise_equity[np.logical_and(nb_raise_equity.index>borders[i], nb_raise_equity.index<borders[i+1])].sum()
            len_equity_batch=len_equity[np.logical_and(len_equity.index>borders[i], len_equity.index<borders[i+1])].sum()
            freq_raise_equity.append(nb_raise_batch/len_equity_batch)
    
        nb_call_equity = data.groupby(by=round(20*data.equity)/20).apply(lambda x: sum(np.logical_and(x.action=='call',x.amount>1)))
        freq_call_equity=[]
        for i in range(len(borders)-1):
            nb_call_batch=nb_call_equity[np.logical_and(nb_call_equity.index>borders[i], nb_call_equity.index<borders[i+1])].sum()
            len_equity_batch=len_equity[np.logical_and(len_equity.index>borders[i], len_equity.index<borders[i+1])].sum()
            freq_call_equity.append(nb_call_batch/len_equity_batch)
    
        nb_check_equity = data.groupby(by=round(20*data.equity)/20).apply(lambda x: sum(np.logical_and(x.action=='call',x.amount<1)))
        freq_check_equity=[]
        for i in range(len(borders)-1):
            nb_check_batch=nb_check_equity[np.logical_and(nb_check_equity.index>borders[i], nb_check_equity.index<borders[i+1])].sum()
            len_equity_batch=len_equity[np.logical_and(len_equity.index>borders[i], len_equity.index<borders[i+1])].sum()
            freq_check_equity.append(nb_check_batch/len_equity_batch)
        
        nb_fold_equity = data.groupby(by=round(20*data.equity)/20).apply(lambda x: sum(x.action=='fold'))
        freq_fold_equity=[]
        for i in range(len(borders)-1):
            nb_fold_batch=nb_fold_equity[np.logical_and(nb_fold_equity.index>borders[i], nb_fold_equity.index<borders[i+1])].sum()
            len_equity_batch=len_equity[np.logical_and(len_equity.index>borders[i], len_equity.index<borders[i+1])].sum()
            freq_fold_equity.append(nb_fold_batch/len_equity_batch)
       
        
        nb_net_output_equity = data.groupby(by=round(20*data.equity)/20).apply(lambda x: sum(((np.sign(x.net_output)+1)/2)*x.net_output))#np.average(((np.sign(x.net_output)+1)/2)*x.net_output))
        net_output_equity=[]
        for i in range(len(borders)-1):
            net_output_equity_batch=nb_net_output_equity[np.logical_and(np.array(nb_net_output_equity.index)>borders[i], np.array(nb_net_output_equity.index)<borders[i+1])].sum()
            len_equity_batch=len_equity[np.logical_and(len_equity.index>borders[i], len_equity.index<borders[i+1])].sum()
            print(len_equity_batch)
            net_output_equity.append(net_output_equity_batch/len_equity_batch)
    
        #FREQ ACTION POS
        
        #if my_network == '6max_full':
        #    unraised_streets_preflop= np.logical_and(np.logical_and(data.call_price<=data.bb, data.preflop==1), 6*data.nb_opps>1.1)
        #elif my_network == '6max_single':
        unraised_streets_preflop=np.logical_and(np.logical_and(data.call_price<=data.bb, data.preflop==1), 6*data.nb_opps>1.1)
        freq_raise_bb = data.where(unraised_streets_preflop).dropna().groupby(by=data.bb).apply(lambda x: sum(x.action=='raise')/len(x))
        freq_call_bb = data.where(unraised_streets_preflop).dropna().groupby(by=data.bb).apply(lambda x: sum(x.action=='call')/len(x))
        freq_fold_bb = data.where(unraised_streets_preflop).dropna().groupby(by=data.bb).apply(lambda x: sum(x.action=='fold')/len(x))
        
        freq_raise_pos = data.where(unraised_streets_preflop).dropna().groupby(by=[data.pos]).apply(lambda x: (sum(np.array((x.action=='raise')+0.1)/np.array(freq_raise_bb[x.bb]+0.1))/len(x)))#
        freq_call_pos = data.where(unraised_streets_preflop).dropna().groupby(by=[data.pos]).apply(lambda x: (sum(np.array((np.logical_and(x.action=='call',x.amount>1))+0.1)/np.array(freq_call_bb[x.bb]+0.1))/len(x)))#
        freq_check_pos = data.where(unraised_streets_preflop).dropna().groupby(by=[data.pos]).apply(lambda x: (sum(np.array((np.logical_and(x.action=='call',x.amount<1))+0.1)/np.array(freq_call_bb[x.bb]+0.1))/len(x)))#
        freq_fold_pos = data.where(unraised_streets_preflop).dropna().groupby(by=[data.pos]).apply(lambda x: (sum(np.array((x.action=='fold')+0.1)/np.array(freq_fold_bb[x.bb]+0.1))/len(x)))#
    
        #print(freq_raise_per_pos)
        #print(data.where(unraised_streets_preflop).dropna().groupby(by=[data.bb, data.pos]).apply(lambda x: len(x)))
    

        #print(freq_raise_street)
        
        print('freq raise :' +str(freq_raise))
        print('freq call :' +str(freq_call))
        print('freq fold :' +str(freq_fold))
        print('avg net output :' +str(avg_net_output))
        print('avg raise value :' +str(avg_raise_value))
        
    
        max_round = min(data.round_id.max(),200)
        
        raise_amount_at_round = raise_amount_at_round.where(lambda x: x.index<=max_round).dropna()
        stack_at_round = stack_at_round.where(lambda x: x.index<=max_round).dropna()
        
        #raise_amount_at_round  = list(smooth(list(raise_amount_at_round),11))
        
        
        missing_round = [int(i) for i in list(np.linspace(1,max_round,max_round)) if i not in stack_at_round.index]
        round_axis = list(range(max_round))
        for i in missing_round:
            round_axis.remove(i)
        
        #plt.p
        #plt.plot(round_axis,raise_amount_at_round)
        
        freq_raise_street = data.groupby(by=data.street).apply(lambda x: sum(x.action=='raise')/len(x))
        freq_check_street = data.groupby(by=data.street).apply(lambda x: sum(np.logical_and(x.action=='call',x.amount<1))/len(x))
        freq_call_street = data.groupby(by=data.street).apply(lambda x: sum(np.logical_and(x.action=='call',x.amount>1))/len(x))
        freq_fold_street = data.groupby(by=data.street).apply(lambda x: sum(x.action=='fold')/len(x))
        
    #freq_raise_street = data.where(data.nb_opps<1.1).dropna().groupby(by=data.street).apply(lambda x: sum(x.action=='raise')/len(x))
    #freq_call_street = data.where(data.nb_opps<1.1).dropna().groupby(by=data.street).apply(lambda x: sum(x.action=='call')/len(x))
    #freq_fold_street = data.where(data.nb_opps<1.1).dropna().groupby(by=data.street).apply(lambda x: sum(x.action=='fold')/len(x))

    ## FIG 1
    plt.ylim([0,100])
    filter_size = 7
    freq_raise_round_ = 100*freq_raise_round.where(lambda x: x.index<=max_round).dropna()
    smooth_freq_raise_round= list(smooth(list(freq_raise_round_),filter_size))
    plt.plot(round_axis, smooth_freq_raise_round, color='#ff6600', alpha=0.7)
             
    freq_call_round_ = 100*freq_call_round.where(lambda x: x.index<=max_round).dropna()
    smooth_freq_call_round= list(smooth(list(freq_call_round_),filter_size))
    plt.plot(round_axis, smooth_freq_call_round, color='blue', alpha=0.7)
    
    freq_check_round_ = 100*freq_check_round.where(lambda x: x.index<=max_round).dropna()
    smooth_freq_check_round= list(smooth(list(freq_check_round_),filter_size))
    plt.plot(round_axis, smooth_freq_check_round, color='green', alpha=0.7)
    
    freq_fold_round_ = 100*freq_fold_round.where(lambda x: x.index<=max_round).dropna()
    smooth_freq_fold_round= list(smooth(list(freq_fold_round_),filter_size))
    plt.plot(round_axis, smooth_freq_fold_round, color='black', alpha=0.7)
    plt.xlabel('Round', fontsize='large')
    plt.ylabel('Action frequency [%]',fontsize='large')
    plt.legend(['Raise','Check','Call','Fold'])
    if my_network == '6max_single':
        plt.savefig('6max_action_freq_round.png', dpi=my_dpi)
    elif my_network=='6max_full':
        plt.savefig('full_6max_action_freq_round_'+str(table_ind)+'.png', dpi=1000)
    ## FIG 2
    fig, ax1 = plt.subplots()
    filter_size=5
    raise_amount_at_round_smooth  = list(smooth(list(raise_amount_at_round),filter_size))
    ax1.plot(round_axis, raise_amount_at_round_smooth,color='#cc6600', alpha=0.8)
    ax1.set_xlabel('Round', fontsize='large')
    # Make the y-axis label, ticks and tick labels match the line color.
    ax1.set_ylabel('Raise value', color='#cc6600', fontsize='large')
    ax1.tick_params('y', colors='#cc6600')
    
    ax2 = ax1.twinx()
    stack_at_round_smooth = list(smooth(list(stack_at_round),filter_size))
    ax2.plot(round_axis,stack_at_round_smooth, color = 'darkgreen', alpha=0.8)
    ax2.set_ylabel('Stack', color='darkgreen', fontsize='large')
    ax2.tick_params('y', colors='darkgreen')
    
    fig.tight_layout()
    plt.show()
    if my_network == '6max_single':
        fig.savefig('6max_raise_stack_round.png', dpi=my_dpi)
    elif my_network=='6max_full':
        fig.savefig('full_6max_raise_stack_round_'+str(table_ind)+'.png', dpi=1000)
        
    ## FIG 3
    fig, ax = plt.subplots()
    filter_size = 3
    freq_openraise_round_ = 100*freq_openraise_round.where(lambda x: x.index<=max_round).dropna()
    smooth_freq_openraise_round= list(smooth(list(freq_openraise_round_),filter_size))
    ax.plot(freq_openraise_round_.index, smooth_freq_openraise_round, color='purple', alpha=0.7)
    
    freq_reraise_round_ = 100*freq_reraise_round.where(lambda x: x.index<=max_round).dropna()
    smooth_freq_reraise_round= list(smooth(list(freq_reraise_round_),filter_size))
    ax.plot(freq_reraise_round_.index, smooth_freq_reraise_round, color='red', alpha=0.7)
    
    ax.legend(['Unraised street', 'Raised street'])
    ax.set_ylabel('Raise frequency [%]', fontsize='large')
    ax.set_xlabel('Round', fontsize='large')
    plt.show()
    if my_network == '6max_single':
        fig.savefig('6max_reraise_round.png', dpi=my_dpi)
    elif my_network=='6max_full':
        fig.savefig('full_6max_reraise_round_'+str(table_ind)+'.png', dpi=1000)
    # FIG 4
    ind = np.arange(len(freq_raise_street)) 
    width=0.17
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - 1.5*width, 100*freq_raise_street, width, label='Raise', color='#ff6600', alpha=0.7)
    rects2 = ax.bar(ind - 0.5*width, 100*freq_call_street, width, label='Call', color='blue', alpha=0.7)
    rects3 = ax.bar(ind +0.5*width, 100*freq_check_street, width, label='Check', color='green', alpha=0.7)
    rects4 = ax.bar(ind + 1.5*width, 100*freq_fold_street, width, label='Fold', color='black', alpha=0.7)
    ax.set_ylabel('Action frequency [%]', fontsize='large')
    ax.legend(['Raise','Call','Check','Fold'], framealpha=0.5, loc='upper center')
    ax.set_xticklabels(['','Preflop','','Flop','','Turn','','River'])
    if my_network == '6max_single':
        fig.savefig('6max_action_street.png', dpi=my_dpi)
    elif my_network=='6max_full':
        fig.savefig('full_6max_action_street_'+str(table_ind)+'.png', dpi=1000)
    
    # FIG 5
    ind = np.arange(len(freq_raise_equity)) 
    width=0.17
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - 1.5*width, 100*np.array(freq_raise_equity), width, label='Raise', color='#ff6600', alpha=0.7)
    rects2 = ax.bar(ind -0.5*width, 100*np.array(freq_call_equity), width, label='Call', color='blue', alpha=0.7)
    rects3 = ax.bar(ind + 0.5*width, 100*np.array(freq_check_equity), width, label='Check', color='green', alpha=0.7)
    rects4 = ax.bar(ind + 1.5*width, 100*np.array(freq_fold_equity), width, label='Fold', color='black', alpha=0.7)
    ax.set_ylabel('Action frequency [%]', fontsize='large')
    ax.legend(['Raise','Call','Check','Fold'], framealpha=0.5, loc='upper center')
    ax.set_xticklabels(['','0 -> 0.75','','0.75 -> 1','','1 -> 1.25','','1.25 -> 6'])
    ax.set_xlabel('Corrected Equity ranges', fontsize='large')
    if my_network == '6max_single':
        fig.savefig('6max_action_equity.png', dpi=my_dpi)
    elif my_network=='6max_full':
        fig.savefig('full_6max_action_equity_'+str(table_ind)+'.png', dpi=1000)
    #FIG 6
    nb_pos_kept=4
    ind = np.arange(nb_pos_kept) 
    width=0.17
    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - 1.5*width, np.array(freq_raise_pos)[:nb_pos_kept], width, label='Raise', color='#ff6600', alpha=0.7)
    rects2 = ax.bar(ind -0.5*width, np.array(freq_call_pos)[:nb_pos_kept], width, label='Call', color='blue', alpha=0.7)
    rects3 = ax.bar(ind +0.5*width, np.array(freq_check_pos)[:nb_pos_kept], width, label='Check', color='green', alpha=0.7)
    rects4 = ax.bar(ind + 1.5*width, np.array(freq_fold_pos)[:nb_pos_kept], width, label='Fold', color='black', alpha=0.7)
    ax.set_ylabel('Action frequency factor', fontsize='large')
    ax.legend(['Raise','Call','Check','Fold'], framealpha=0.5, loc='upper center')
    ax.set_xticklabels(['','0','','-1','','-2','','-3'])
    ax.set_xlabel('Relative position to big-blind', fontsize='large')
    ax.set_ylim([0.5,1.2])
    if my_network == '6max_single':
        fig.savefig('6max_action_pos.png', dpi=my_dpi)
    elif my_network=='6max_full':
        fig.savefig('full_6max_action_pos_'+str(table_ind)+'.png', dpi=1000)
        
    