#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 24 23:57:43 2019

@author: cyril
"""
import sys
#sys.path.append('../neural-net')
sys.path.append('../PyPokerEngine_fork')
from pypokerengine.players import BasePokerPlayer
import torch
from torch import nn
import os
from utils_bot import get_tot_pot, comp_hand_equity, decision_algo, comp_is_BB, comp_n_act_players, print_cards, print_state
import re
from collections import OrderedDict
from torch.nn import functional as F
import random

my_verbose_upper = False
write_details = False

from utils_io import write_declare_action_state, write_round_start_state, write_round_result_state, find_action_id, find_round_id
#mkl.set_num_threads(1)

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
        self.i_opp = i_opp
        self.i_gen = i_gen
        self.u_opp = i_opp.copy()
        self.u_gen = i_gen.copy()

    def forward(self, x):
        x_opp_out, (self.u_opp['h0'], self.u_opp['c0']) = self.LSTM_opp(x, (self.u_opp['h0'], self.u_opp['c0']))
        #print('x_opp_out: '+str(x_opp_out[0][0][:20]))
        x_opp_out = self.LSTM_opp(x)
        x_gen_all, (self.u_gen['h0_0'], self.u_gen['c0_0']) = self.LSTM_gen[0](x, (self.u_gen['h0_0'], self.u_gen['c0_0']))
        for i in range(1,10):
            x_gen, (self.u_gen['h0_'+str(i)], self.u_gen['c0_'+str(i)]) = self.LSTM_gen[i](x, (self.u_gen['h0_'+str(i)], self.u_gen['c0_'+str(i)]))
            #x_gen_all = torch.cat((x_gen_all,self.LSTM_gen[i](x, (i_gen['h0_'+str(i)].view(1,1,10), i_gen['c0_'+str(i)].view(1,1,10)))[0].view(1,1,1,-1)),0)
            x_gen_all = torch.cat((x_gen_all,x_gen),0)

        x_gen_out = x_gen_all.view(1,1,-1)
        x_lin_h = torch.tanh(self.lin_dec_1(torch.cat((x_gen_out,x_opp_out[0]),2)))
        x_out = torch.tanh(self.lin_dec_2(x_lin_h))
        return x_out
    
    def reset_u_opp(self):
        self.u_opp = self.i_opp.copy()
    def reset_u_gen(self):
        self.u_gen = self.i_gen.copy()
    def reset(self):
        self.reset_u_opp()
        self.reset_u_gen()
        return



class LSTMBot(BasePokerPlayer):  
    def __init__(self, id_=1, gen_dir='./simul_data/simul_0/gen_0', full_dict = None, game='HU'):
    
        self.game=game
        if game =='HU':
            if full_dict == None:
                i_opp = self.init_i_opp()
                i_gen = self.init_i_gen()
                self.model = Net(i_opp,i_gen)
                self.state_dict = next(self.model.modules()).state_dict()   #weights are automaticaly generated
                full_dict_ = self.state_dict.copy()
                full_dict_.update(i_opp), full_dict_.update(i_gen)    
                self.full_dict = full_dict_
            else:
                self.full_dict= full_dict
                self.state_dict, i_opp, i_gen = get_sep_dicts(full_dict)
                self.model = Net(i_opp,i_gen)
                self.model.load_state_dict(self.state_dict)
            self.id = id_
            self.gen_dir = gen_dir
            #if not os.path.exists(self.gen_dir+'/bots/'+str(self.id)):
            #    os.makedirs(self.gen_dir+'/bots/'+str(self.id)) 
            self.opponent = None
            
        elif game =='6max':
            pass



    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        self.new_round_handle(round_state)
        input_tensor = self.prep_input(hole_card, round_state, valid_actions)
        #print('input tensor: '+str(input_tensor))
        net_output = self.net_predict(input_tensor)
        #print('net output: ' +str(net_output))
            
        action, amount = decision_algo(net_output=net_output, round_state=round_state, valid_actions = valid_actions,
                                       i_stack = self.i_stack, my_uuid = self.uuid, verbose = my_verbose_upper)

        if write_details:
            write_declare_action_state(action_id = self.action_id, round_id = self.round_id, valid_actions = valid_actions,
                               hole_card = hole_card, round_state = round_state, strat=None, action=action, amount = amount,
                               csv_file = self.gen_dir+'/bots/'+str(self.id)+'/'+str(self.opponent)+'_declare_action_state.csv')
            self.action_id+=1
        if random.random() < 1:
            print_cards(hole_card = hole_card, round_state=round_state)
            print_state(net_output=net_output, action=action, amount=amount)
        
        return action, amount   # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        self.i_stack = game_info['rule']['initial_stack']
        if write_details:
            self.action_id = find_action_id(csv_file = self.gen_dir+'/bots/'+str(id)+'/'+str(self.opponent)+'_declare_action_state.csv')
            self.round_id = find_round_id(csv_file = self.gen_dir+'/bots/'+str(id)+'/'+str(self.opponent)+'_round_result_state.csv')
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        if write_details:
            write_round_start_state(round_id = self.round_id, seats = seats, csv_file = self.gen_dir+'/bots/'+str(self.id)+'/'+str(self.opponent)+'_round_start_state.csv')
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        if write_details:
            write_round_result_state(round_id = self.round_id, winners = winners,
                             hand_info = hand_info, round_state = round_state, csv_file = self.gen_dir+'/bots/'+str(self.id)+'/'+str(self.opponent)+'_round_result_state.csv')
            self.round_id+=1
        pass
    
            
    def init_i_opp(self):
        i_opp_keys = ['h0','c0']
        i_opp = OrderedDict()
        for key in i_opp_keys:
            i_opp[key]=torch.randn(50).view(1,1,50)
        return i_opp
    
    def init_i_gen(self):
        i_gen_keys = ['h0_'+str(i) for i in range(10)]+['c0_'+str(i) for i in range(10)]
        i_gen = OrderedDict()
        for key in i_gen_keys:
            i_gen[key]=torch.randn(10).view(1,1,10)
        return i_gen
    
    def new_round_handle(self, round_state):
        if round_state['street'] =='preflop' and len([action['action'] for action in round_state['action_histories']['preflop'] if action['uuid']==self.uuid and not(action['action'] in ['BIGBLIND', 'SMALLBLIND'])]) == 0:
            self.model.reset_u_gen()
        return
    
    def prep_input(self, hole_card, round_state, valid_actions):
        n_act_players = comp_n_act_players(round_state)
        
        inputs = [0,]*8
        #setting street one-hot encoding
        streets =  ['preflop', 'flop', 'turn', 'river']
        street_ind = streets.index(round_state['street'])
        inputs[street_ind] = 1
        
        #setting hand equity
        inputs[4] = comp_hand_equity(hole_card = hole_card, community_card = round_state['community_card'], n_act_players = n_act_players)
        
        #setting my investment in hand
        my_invest = 0 
        for street_key, street_hist in zip(round_state['action_histories'].keys(), round_state['action_histories'].values()):
            #for i in range(len(street_hist),0,-1):
            street_invest_arr = [action['amount'] for action in street_hist if action['uuid']==self.uuid]
            if len(street_invest_arr)!=0:
                street_invest = street_invest_arr[-1]
                my_invest +=  street_invest
        inputs[5] = my_invest /self.i_stack

        
        #setting investment of all opponents
        tot_pot = get_tot_pot(round_state['pot'])
        inputs[6] = (tot_pot-my_invest)/self.i_stack
        
        #setting my pot-odd
        call_price = [action['amount'] for action in valid_actions if action['action']=='call'][0]
        inputs[7] = call_price/(call_price+tot_pot)

        return torch.Tensor(inputs).view(1, 1, -1)
 
    
    def clear_log(self):
        for logtype in ['declare_action_state','round_start_state','round_result_state']:
            if self.gen_dir != None and os.path.exists(self.gen_dir+'/bots/'+str(self.id)+'/'+str(self.opponent)+'_'+logtype+'.csv'):
                os.remove(self.gen_dir+'/bots/'+str(self.id)+'/'+str(self.opponent)+'_'+logtype+'.csv')
            
    def net_predict(self, input_tensor):
        net_output = self.model(input_tensor)
        return net_output.squeeze().item()
    

    
def get_sep_dicts(full_dict):
    state_dict = OrderedDict()
    i_opp = OrderedDict()
    i_gen = OrderedDict()
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
    
    
def setup_ai():
    return LSTMBot()