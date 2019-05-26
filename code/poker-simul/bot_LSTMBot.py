#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 24 23:57:43 2019

@author: cyril
"""
import sys
sys.path.append('../neural-net')
from pypokerengine.players import BasePokerPlayer
import torch
from torch import nn
from functools import reduce
from utils import comp_tot_params, get_flat_params, get_dict_sizes, get_full_dict, get_sep_dicts
import pickle
import random

my_verbose_upper = True

# Import ctypes, it is native to python
import numpy.ctypeslib as ctl
import ctypes
libname = 'libhandequity.so'
# The path may have to be changed
libdir = '../OMPEval_fork/lib/'
lib = ctl.load_library(libname, libdir)
# Defining the python function from the library
omp_hand_equity = lib.hand_equity
# Determining its arguments and return types
omp_hand_equity.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool]
omp_hand_equity.restype = ctypes.c_double
nb_board_cards = 5 # Default is 5. If = 3, showdown is at flop
std_err_tol = 10**-3 # Default is 10**-5. This is the std in % at which the hand equity will be returned


class Net(nn.Module):
    def __init__(self, i_opp, i_gen):
        super(Net, self).__init__()
        self.LSTM_opp = nn.LSTM(input_size =8, hidden_size = 50, num_layers=1)
        self.LSTM_gen = []
        for i in range(10):
            self.LSTM_gen.append(nn.LSTM(8, 10))
        self.LSTM_gen = nn.ModuleList(self.LSTM_gen)
        self.lin_dec_1 = nn.Linear(150, 75)
        self.lin_dec_2 = nn.Linear(75, 1)
        self.f_gen = i_gen
        self.i_opp = i_opp
        self.i_gen = i_gen

    def forward(self, x):
        x_opp_out, (self.i_opp['h0'], self.i_opp['c0']) = self.LSTM_opp(x, (self.i_opp['h0'], self.i_opp['c0']))
        x_opp_out = self.LSTM_opp(x)
        x_gen_all, (self.i_gen['h0_0'], self.i_gen['c0_0']) = self.LSTM_gen[0](x, (self.i_gen['h0_0'], self.i_gen['c0_0']))
        for i in range(1,10):
            x_gen, (self.i_gen['h0_'+str(i)], self.i_gen['c0_'+str(i)]) = self.LSTM_gen[i](x, (self.i_gen['h0_'+str(i)], self.i_gen['c0_'+str(i)]))
            #x_gen_all = torch.cat((x_gen_all,self.LSTM_gen[i](x, (i_gen['h0_'+str(i)].view(1,1,10), i_gen['c0_'+str(i)].view(1,1,10)))[0].view(1,1,1,-1)),0)
            x_gen_all = torch.cat((x_gen_all,x_gen),0)

        x_gen_out = x_gen_all.view(1,1,-1)
        x_lin_h = self.lin_dec_1(torch.cat((x_gen_out,x_opp_out[0]),2))
        x_out = self.lin_dec_2(x_lin_h)
        return x_out
    def reset_i_gen(self):
        self.i_gen = self.f_gen


class LSTMBot(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"
    def __init__(self, full_dict):
    
        if full_dict == None:
            i_opp = self.init_i_opp()
            i_gen = self.init_i_gen()
            self.model = Net(i_opp,i_gen)
            self.state_dict = next(self.model.modules()).state_dict()   #weights are automaticaly generated
        else:
            self.state_dict, i_opp, i_gen = get_sep_dicts(full_dict)
            self.model = Net(i_opp,i_gen)

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        self.check_reset(round_state)
        input_tensor = self.prep_input(hole_card, round_state, valid_actions)
        net_output = self.net_predict(input_tensor)
        action, amount = self.decision_algo(net_output,valid_actions,BB=2*round_state['small_blind_amount'])
        
        return action, amount   # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        self.i_stack = game_info['rule']['initial_stack']
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
    
            
    def init_i_opp(self):
        i_opp_keys = ['h0','c0']
        i_opp = {}
        for key in i_opp_keys:
            i_opp[key]=torch.randn(50).view(1,1,50)
        return i_opp
    
    def init_i_gen(self):
        i_gen_keys = ['h0_'+str(i) for i in range(10)]+['c0_'+str(i) for i in range(10)]
        i_gen = {}
        for key in i_gen_keys:
            i_gen[key]=torch.randn(10).view(1,1,10)
        return i_gen
    
    def check_reset(self, round_state):
        if round_state['street'] =='preflop' and len([action['action'] for action in round_state['action_histories']['preflop'] if action['uuid']==self.uuid and not(action['action'] in ['BIGBLIND', 'SMALLBLIND'])]) == 0:
            print('new_round')
            self.model.reset_i_gen()
    
    def prep_input(self, hole_card, round_state, valid_actions):
        n_act_players = sum([player['state']=='participating' for player in round_state['seats']])
        
        inputs = [0,]*8
        #setting street one-hot encoding
        streets =  ['preflop', 'flop', 'turn', 'river']
        street_ind = streets.index(round_state['street'])
        inputs[street_ind] = 1
        
        #setting hand equity
        nb_board_river = 5
        inputs[4] = omp_hand_equity(format_cards(hole_card).encode(), format_cards(round_state['community_card']).encode(), 
                                     n_act_players, nb_board_river, std_err_tol, False)
        
        #setting 'flop' hand equity
        #nb_board_flop = 3
        #inputs[4] = omp_hand_equity(format_cards(hole_card).encode(), format_cards(round_state['community_card']).encode(), 
        #                             n_act_players, nb_board_flop, std_err_tol, False)
        
        #setting my investment in hand
        my_invest = 0 
        for street_key, street_hist in zip(round_state['action_histories'].keys(), round_state['action_histories'].values()):
            #for i in range(len(street_hist),0,-1):
            street_invest_arr = [action['amount'] for action in street_hist if action['uuid']==self.uuid]
            if len(street_invest_arr)!=0:
                """
                if street_key=='preflop' and len(street_invest_arr)>=2:
                    street_invest =max((2*round_state['small_blind_amount'],street_invest_arr[-1]))
                else:
                    street_invest = street_invest_arr[-1]
                """
                street_invest = street_invest_arr[-1]
                my_invest +=  street_invest
        inputs[5] = my_invest /self.i_stack
        
        #setting all opponents investment
        tot_pot = reduce((lambda x1,x2: x1+x2), [round_state['pot'][key]['amount'] for key in round_state['pot'].keys() if len(round_state['pot'][key])!=0])
        inputs[6] = (tot_pot-my_invest)/self.i_stack
        
        #setting my pot-odd
        call_price = [action['amount'] for action in valid_actions if action['action']=='call'][0]
        inputs[7] = call_price/(call_price+tot_pot)
        
        #setting nb of active players
        #inputs[7] = self.n_act_players     
        print(inputs)
        
        return torch.Tensor(inputs).view(1, 1, -1)
    
    def net_predict(self, input_tensor):
        net_output = self.model(input_tensor)
        return net_output.squeeze().item()
    
    def decision_algo(self, net_output, valid_actions, BB):
        print(net_output)
        y = net_output*self.i_stack
        call_price = [action['amount'] for action in valid_actions if action['action']=='call'][0]
        min_raise = [action['amount']['min'] for action in valid_actions if action['action']=='raise'][0]
        if y<call_price:
            if call_price==0:
                action='call'
                amount = 0
            else:
                action='fold'
                amount = 0
        elif y<min_raise:
            action = 'call'
            amount= call_price
        else:
            #action = 'raise'
            action, amount = self.raise_in_limits(BB * round(y/BB), valid_actions)
        return action, amount
    
    def raise_in_limits(self, amount, valid_actions):
        #if no raise available, calling
        if [item for item in valid_actions if item['action'] == 'raise'][0]['amount']['max']==-1:
            action_in_limits = 'call'
            amount_in_limits = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
        else:
            action_in_limits = 'raise'
            max_raise = [item for item in valid_actions if item['action'] == 'raise'][0]['amount']['max']
            min_raise = [item for item in valid_actions if item['action'] == 'raise'][0]['amount']['min']
            if amount>max_raise:
                if(my_verbose_upper):
                    print('Going all in')
                amount_in_limits = max_raise
            elif amount<min_raise:
                amount_in_limits = min_raise
            else:
                amount_in_limits = amount
        return action_in_limits, amount_in_limits
    
def format_cards(cards):
    if cards != []:
        formatted_cards =  reduce((lambda x1,x2: x1+x2), [card[1]+card[0].lower() for card in cards])
    else:
        formatted_cards = ""
    return formatted_cards
    
def setup_ai():
    return LSTMBot()