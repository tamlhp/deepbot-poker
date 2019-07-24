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
import math


def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_extended = np.hstack(([y[0],]*int(box_pts/2),y,[y[-1],]*int(box_pts/2)))
    y_smooth = np.convolve(y_extended, box, mode='valid')
    return y_smooth

print('## Starting ##')
bot_id = 1
my_network = '6max_full'
table_ind=0
gen=250

my_dpi =100

if my_network=='6max_single':
    data_dir = '6max_single_250'
    nb_opps=1
    fig_1, ax_1 = plt.subplots()
    fig_2, ax_2 = plt.subplots()
    axSecond=0
    fig_3, ax_3 = plt.subplots()
    fig_4, ax_4 = plt.subplots()
    fig_5, ax_5 = plt.subplots()
    fig_6, ax_6 = plt.subplots()
elif my_network=='6max_full':
    nb_opps=4
    titles=['Loose-Passive','Tight-Passive','Loose-Agressive','Tight-Agressive']
    fig_1, axes_1 = plt.subplots(nrows=2,ncols=2)
    fig_2, axes_2 = plt.subplots(nrows=2,ncols=2)
    axSecond=[0,]*nb_opps
    fig_3, axes_3 = plt.subplots(nrows=2,ncols=2)
    fig_4, axes_4 = plt.subplots(nrows=2,ncols=2)
    fig_5, axes_5 = plt.subplots(nrows=2,ncols=2)
    fig_6, axes_6 = plt.subplots(nrows=2,ncols=2)
write_details= True
if my_network =='6max_single' or my_network=='6max_full':
    for k in range(nb_opps):
        table_ind=k
        if my_network=='6max_full':
            data_dir = '6max_full_'+str(gen)+'_'+str(table_ind)
        if True:
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
            freq_call_bb = data.where(unraised_streets_preflop).dropna().groupby(by=data.bb).apply(lambda x: sum(np.logical_and(x.action=='call',x.amount>1))/len(x))
            freq_check_bb = data.where(unraised_streets_preflop).dropna().groupby(by=data.bb).apply(lambda x: sum(np.logical_and(x.action=='call',x.amount<1))/len(x))
            freq_fold_bb = data.where(unraised_streets_preflop).dropna().groupby(by=data.bb).apply(lambda x: sum(x.action=='fold')/len(x))

            freq_raise_pos = data.where(unraised_streets_preflop).dropna().groupby(by=[data.pos]).apply(lambda x: (sum(np.array((x.action=='raise')+0.1)/np.array(freq_raise_bb[x.bb]+0.1))/len(x)))#
            freq_call_pos = data.where(unraised_streets_preflop).dropna().groupby(by=[data.pos]).apply(lambda x: (sum(np.array((np.logical_and(x.action=='call',x.amount>1))+0.1)/np.array(freq_call_bb[x.bb]+0.1))/len(x)))#
            freq_check_pos = data.where(unraised_streets_preflop).dropna().groupby(by=[data.pos]).apply(lambda x: (sum(np.array((np.logical_and(x.action=='call',x.amount<1))+0.1)/np.array(freq_check_bb[x.bb]+0.1))/len(x)))#
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
        filter_size = 7
        freq_raise_round_ = 100*freq_raise_round.where(lambda x: x.index<=max_round).dropna()
        smooth_freq_raise_round= list(smooth(list(freq_raise_round_),filter_size))

        freq_call_round_ = 100*freq_call_round.where(lambda x: x.index<=max_round).dropna()
        smooth_freq_call_round= list(smooth(list(freq_call_round_),filter_size))

        freq_check_round_ = 100*freq_check_round.where(lambda x: x.index<=max_round).dropna()
        smooth_freq_check_round= list(smooth(list(freq_check_round_),filter_size))

        freq_fold_round_ = 100*freq_fold_round.where(lambda x: x.index<=max_round).dropna()
        smooth_freq_fold_round= list(smooth(list(freq_fold_round_),filter_size))

        if my_network == '6max_single':
            ax_1.set_ylim([0,100])
            ax_1.plot(round_axis, smooth_freq_raise_round, color='#ff6600', alpha=0.7)
            ax_1.plot(round_axis, smooth_freq_call_round, color='blue', alpha=0.7)
            ax_1.plot(round_axis, smooth_freq_check_round, color='green', alpha=0.7)
            ax_1.plot(round_axis, smooth_freq_fold_round, color='black', alpha=0.7)
            ax_1.set_xlabel('Hand', fontsize='large')
            ax_1.set_ylabel('Action frequency [%]',fontsize='large')


        elif my_network=='6max_full':
            axes_1[math.floor(k/2)][k%2].set_ylim([0,100])
            axes_1[math.floor(k/2)][k%2].plot(round_axis, smooth_freq_raise_round, color='#ff6600', alpha=0.7)
            axes_1[math.floor(k/2)][k%2].plot(round_axis, smooth_freq_call_round, color='blue', alpha=0.7)
            axes_1[math.floor(k/2)][k%2].plot(round_axis, smooth_freq_check_round, color='green', alpha=0.7)
            axes_1[math.floor(k/2)][k%2].plot(round_axis, smooth_freq_fold_round, color='black', alpha=0.7)
            axes_1[math.floor(k/2)][k%2].set_title(titles[k], fontweight='black')
            if math.floor(k/2)==0:
                axes_1[math.floor(k/2)][k%2].set_xlabel('')
                axes_1[math.floor(k/2)][k%2].set_xticks([])
            else:
                axes_1[math.floor(k/2)][k%2].set_xlabel('Hand', fontsize='large')
            if k%2 ==0:
                axes_1[math.floor(k/2)][k%2].set_ylabel('Action freq [%]',fontsize='large')
            else:
                axes_1[math.floor(k/2)][k%2].set_ylabel('')
                axes_1[math.floor(k/2)][k%2].set_yticks([])
            if k==0:
                axes_1[math.floor(k/2)][k%2].legend(['Raise','Call','Check','Fold'], loc='upper left')


        ## FIG 2
        filter_size=5
        raise_amount_at_round_smooth  = list(smooth(list(raise_amount_at_round),filter_size))

        stack_at_round_smooth = list(smooth(list(stack_at_round),filter_size))
        if my_network == '6max_single':
            ax_2.plot(round_axis, raise_amount_at_round_smooth,color='#cc6600', alpha=0.8)
            ax_2.set_xlabel('Hand', fontsize='large')
            # Make the y-axis label, ticks and tick labels match the line color.
            ax_2.set_ylabel('Raise amount', color='#cc6600', fontsize='large')
            ax_2.tick_params('y', colors='#cc6600')

            axSecond = ax_2.twinx()
            axSecond.plot(round_axis,stack_at_round_smooth, color = 'darkgreen', alpha=0.8)
            axSecond.set_ylabel('Stack', color='darkgreen', fontsize='large')
            axSecond.tick_params('y', colors='darkgreen')

            fig_2.tight_layout()
        elif my_network=='6max_full':
            axes_2[math.floor(k/2)][k%2].plot(round_axis, raise_amount_at_round_smooth,color='#cc6600', alpha=0.8)
            axes_2[math.floor(k/2)][k%2].set_title(titles[k], fontweight='black')
            axes_2[math.floor(k/2)][k%2].set_ylim([0,3500])

            axSecond[k] = axes_2[math.floor(k/2)][k%2].twinx()
            axSecond[k].set_ylim([0,6000])
            axSecond[k].plot(round_axis,stack_at_round_smooth, color = 'darkgreen', alpha=0.8)
            if math.floor(k/2)==0:
                axes_2[math.floor(k/2)][k%2].set_xlabel('')
                axes_2[math.floor(k/2)][k%2].set_xticks([])
            else:
                axes_2[math.floor(k/2)][k%2].set_xlabel('Hand', fontsize='large')
            if k%2 ==0:
                axes_2[math.floor(k/2)][k%2].set_ylabel('Raise amount', color='#cc6600', fontsize='large')
                axes_2[math.floor(k/2)][k%2].tick_params('y', colors='#cc6600')
                axSecond[k].set_ylabel('')
                axSecond[k].set_yticks([])
                axSecond[k].tick_params([])
            else:
                axSecond[k].set_ylabel('Stack', color='darkgreen', fontsize='large')
                axSecond[k].tick_params('y', colors='darkgreen')
                axes_2[math.floor(k/2)][k%2].set_ylabel('')
                axes_2[math.floor(k/2)][k%2].set_yticks([])
                axes_2[math.floor(k/2)][k%2].tick_params([])
            fig_2.tight_layout()




        ## FIG 3
        fig, ax = plt.subplots()
        filter_size = 3
        freq_openraise_round_ = 100*freq_openraise_round.where(lambda x: x.index<=max_round).dropna()
        smooth_freq_openraise_round= list(smooth(list(freq_openraise_round_),filter_size))
        freq_reraise_round_ = 100*freq_reraise_round.where(lambda x: x.index<=max_round).dropna()
        smooth_freq_reraise_round= list(smooth(list(freq_reraise_round_),filter_size))

        if my_network == '6max_single':
            ax_3.plot(freq_openraise_round_.index, smooth_freq_openraise_round, color='purple', alpha=0.7)
            ax_3.plot(freq_reraise_round_.index, smooth_freq_reraise_round, color='red', alpha=0.7)
            ax_3.legend(['Unraised street', 'Raised street'])
            ax_3.set_ylabel('Raise frequency [%]', fontsize='large')
            ax_3.set_xlabel('Hand', fontsize='large')
        elif my_network=='6max_full':
            axes_3[math.floor(k/2)][k%2].plot(freq_openraise_round_.index, smooth_freq_openraise_round, color='purple', alpha=0.7)
            axes_3[math.floor(k/2)][k%2].plot(freq_reraise_round_.index, smooth_freq_reraise_round, color='red', alpha=0.7)
            axes_3[math.floor(k/2)][k%2].set_title(titles[k], fontweight='black')
            axes_3[math.floor(k/2)][k%2].set_ylim([0,100])

            if math.floor(k/2)==0:
                axes_3[math.floor(k/2)][k%2].set_xlabel('')
                axes_3[math.floor(k/2)][k%2].set_xticks([])
            else:
                axes_3[math.floor(k/2)][k%2].set_xlabel('Hand', fontsize='large')
            if k%2 ==0:
                axes_3[math.floor(k/2)][k%2].set_ylabel('Raise freq [%]', fontsize='large')
            else:
                axes_3[math.floor(k/2)][k%2].set_ylabel('')
                axes_3[math.floor(k/2)][k%2].set_yticks([])
            if k==0:
                axes_3[math.floor(k/2)][k%2].legend(['Unraised street', 'Raised street'], loc= 'upper left')
        # FIG 4
        ind = np.arange(len(freq_raise_street))
        width=0.17
        fig, ax = plt.subplots()

        if my_network == '6max_single':
            ax_4.bar(ind - 1.5*width, 100*freq_raise_street, width, label='Raise', color='#ff6600', alpha=0.7)
            ax_4.bar(ind - 0.5*width, 100*freq_call_street, width, label='Call', color='blue', alpha=0.7)
            ax_4.bar(ind +0.5*width, 100*freq_check_street, width, label='Check', color='green', alpha=0.7)
            ax_4.bar(ind + 1.5*width, 100*freq_fold_street, width, label='Fold', color='black', alpha=0.7)

            ax_4.set_ylabel('Action frequency [%]', fontsize='large')
            ax_4.legend(['Raise','Call','Check','Fold'], framealpha=0.5, loc='upper center')
            ax_4.set_xticklabels(['','','Preflop','','Flop','','Turn','','River'])
            ax_4.set_xlabel('Street', fontsize='large')
        elif my_network=='6max_full':
            axes_4[math.floor(k/2)][k%2].set_title(titles[k], fontweight='black')
            axes_4[math.floor(k/2)][k%2].bar(ind - 1.5*width, 100*freq_raise_street, width, label='Raise', color='#ff6600', alpha=0.7)
            axes_4[math.floor(k/2)][k%2].bar(ind - 0.5*width, 100*freq_call_street, width, label='Call', color='blue', alpha=0.7)
            axes_4[math.floor(k/2)][k%2].bar(ind +0.5*width, 100*freq_check_street, width, label='Check', color='green', alpha=0.7)
            axes_4[math.floor(k/2)][k%2].bar(ind + 1.5*width, 100*freq_fold_street, width, label='Fold', color='black', alpha=0.7)
            axes_4[math.floor(k/2)][k%2].set_ylim([0,100])

            if math.floor(k/2)==0:
                axes_4[math.floor(k/2)][k%2].set_xlabel('')
                axes_4[math.floor(k/2)][k%2].set_xticks([])
                axes_4[math.floor(k/2)][k%2].set_xticklabels([])
            else:
                axes_4[math.floor(k/2)][k%2].set_xlabel('Street', fontsize='large')
                axes_4[math.floor(k/2)][k%2].set_xticklabels(['','Preflop','Flop','Turn','River'])
            if k%2 ==0:
                axes_4[math.floor(k/2)][k%2].set_ylabel('Action freq [%]', fontsize='large')
            else:
                axes_4[math.floor(k/2)][k%2].set_ylabel('')
                axes_4[math.floor(k/2)][k%2].set_yticks([])

            if k==0:
                axes_4[math.floor(k/2)][k%2].legend(['Raise','Call','Check','Fold'], framealpha=0.5, loc='upper left')
        # FIG 5
        ind = np.arange(len(freq_raise_equity))
        width=0.17
        fig, ax = plt.subplots()
        if my_network == '6max_single':

            ax_5.bar(ind - 1.5*width, 100*np.array(freq_raise_equity), width, label='Raise', color='#ff6600', alpha=0.7)
            ax_5.bar(ind -0.5*width, 100*np.array(freq_call_equity), width, label='Call', color='blue', alpha=0.7)
            ax_5.bar(ind + 0.5*width, 100*np.array(freq_check_equity), width, label='Check', color='green', alpha=0.7)
            ax_5.bar(ind + 1.5*width, 100*np.array(freq_fold_equity), width, label='Fold', color='black', alpha=0.7)

            ax_5.set_ylabel('Action freq [%]', fontsize='large')
            ax_5.legend(['Raise','Call','Check','Fold'], framealpha=0.5, loc='upper center')
            ax_5.set_xticklabels(['','','0 -> 0.75','','0.75 -> 1','','1 -> 1.25','','1.25 -> 6'])
            ax_5.set_xlabel('Adapted Equity range', fontsize='large')

        elif my_network=='6max_full':
            axes_5[math.floor(k/2)][k%2].set_title(titles[k], fontweight='black')
            axes_5[math.floor(k/2)][k%2].bar(ind - 1.5*width, 100*np.array(freq_raise_equity), width, label='Raise', color='#ff6600', alpha=0.7)
            axes_5[math.floor(k/2)][k%2].bar(ind -0.5*width, 100*np.array(freq_call_equity), width, label='Call', color='blue', alpha=0.7)
            axes_5[math.floor(k/2)][k%2].bar(ind + 0.5*width, 100*np.array(freq_check_equity), width, label='Check', color='green', alpha=0.7)
            axes_5[math.floor(k/2)][k%2].bar(ind + 1.5*width, 100*np.array(freq_fold_equity), width, label='Fold', color='black', alpha=0.7)
            axes_5[math.floor(k/2)][k%2].set_ylim([0,100])

            if math.floor(k/2)==0:
                axes_5[math.floor(k/2)][k%2].set_xlabel('')
                axes_5[math.floor(k/2)][k%2].set_xticks([])
                axes_5[math.floor(k/2)][k%2].set_xticklabels([])
            else:
                axes_5[math.floor(k/2)][k%2].set_xlabel('Adapted Equity range', fontsize='large')
                axes_5[math.floor(k/2)][k%2].set_xticklabels(['','0->0.75','0.75->1','1->1.25','1.25->6'], fontsize='small')
            if k%2 ==0:
                axes_5[math.floor(k/2)][k%2].set_ylabel('Action freq [%]', fontsize='large')
            else:
                axes_5[math.floor(k/2)][k%2].set_ylabel('')
                axes_5[math.floor(k/2)][k%2].set_yticks([])

            if k==0:
                axes_5[math.floor(k/2)][k%2].legend(['Raise','Call','Check','Fold'], framealpha=0.5, loc='upper left')

        #FIG 6
        nb_pos_kept=4
        ind = np.arange(nb_pos_kept)
        width=0.17
        fig, ax = plt.subplots()

        if my_network == '6max_single':
            ax_6.bar(ind - 1.5*width, 100*np.array(freq_raise_pos)[:nb_pos_kept], width, label='Raise', color='#ff6600', alpha=0.7)
            ax_6.bar(ind -0.5*width, 100*np.array(freq_call_pos)[:nb_pos_kept], width, label='Call', color='blue', alpha=0.7)
            ax_6.bar(ind +0.5*width, 100*np.array(freq_check_pos)[:nb_pos_kept], width, label='Check', color='green', alpha=0.7)
            ax_6.bar(ind + 1.5*width, 100*np.array(freq_fold_pos)[:nb_pos_kept], width, label='Fold', color='black', alpha=0.7)

            ax_6.set_ylabel('Blind-normalized action frequency', fontsize='large')
            ax_6.legend(['Raise','Call','Check','Fold'], framealpha=0.5, loc='upper center')
            ax_6.set_xticklabels(['','','0','','-1','','-2','','-3'])
            ax_6.set_xlabel('Relative position to big-blind', fontsize='large')
            ax_6.set_ylim([50,120])
        elif my_network=='6max_full':
            axes_6[math.floor(k/2)][k%2].set_title(titles[k], fontweight='black')
            axes_6[math.floor(k/2)][k%2].bar(ind - 1.5*width, 100*np.array(freq_raise_pos)[:nb_pos_kept], width, label='Raise', color='#ff6600', alpha=0.7)
            axes_6[math.floor(k/2)][k%2].bar(ind -0.5*width, 100*np.array(freq_call_pos)[:nb_pos_kept], width, label='Call', color='blue', alpha=0.7)
            axes_6[math.floor(k/2)][k%2].bar(ind +0.5*width, 100*np.array(freq_check_pos)[:nb_pos_kept], width, label='Check', color='green', alpha=0.7)
            axes_6[math.floor(k/2)][k%2].bar(ind + 1.5*width, 100*np.array(freq_fold_pos)[:nb_pos_kept], width, label='Fold', color='black', alpha=0.7)
            axes_6[math.floor(k/2)][k%2].set_ylim([50,150])


            if math.floor(k/2)==0:
                axes_6[math.floor(k/2)][k%2].set_xlabel('')
                axes_6[math.floor(k/2)][k%2].set_xticks([])
                axes_6[math.floor(k/2)][k%2].set_xticklabels([])
            else:
                axes_6[math.floor(k/2)][k%2].set_xticklabels(['','0','-1','-2','-3'])
                axes_6[math.floor(k/2)][k%2].set_xlabel('Relative position to big-blind', fontsize='large')
            if k%2 ==0:
                axes_6[math.floor(k/2)][k%2].set_ylabel('BNAF [%]', fontsize='large')
            else:
                axes_6[math.floor(k/2)][k%2].set_ylabel('')
                axes_6[math.floor(k/2)][k%2].set_yticks([])

            if k==0:
                axes_6[math.floor(k/2)][k%2].legend(['Raise','Call','Check','Fold'], framealpha=0.5, loc='upper left')

    if my_network=='6max_single':
        fig_1.savefig('./single/6max_action_freq_round.png', dpi=my_dpi)
        fig_2.savefig('./single/6max_raise_stack_round.png', dpi=my_dpi)
        fig_3.savefig('./single/6max_reraise_round.png', dpi=my_dpi)
        fig_4.savefig('./single/6max_action_street.png', dpi=my_dpi)
        fig_5.savefig('./single/6max_action_equity.png', dpi=my_dpi)
        fig_6.savefig('./single/6max_action_pos.png', dpi=my_dpi)

    if my_network=='6max_full':
        fig_1.savefig('./full/full_6max_action_freq_round.png', dpi=my_dpi)
        fig_2.savefig('./full/full_6max_raise_stack_round.png', dpi=my_dpi)
        fig_3.savefig('./full/full_6max_reraise_round.png', dpi=my_dpi)
        fig_4.savefig('./full/full_6max_action_street.png', dpi=my_dpi)
        fig_5.savefig('./full/full_6max_action_equity.png', dpi=my_dpi)
        fig_6.savefig('./full/full_6max_action_pos.png', dpi=my_dpi)
