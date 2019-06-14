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
from utils_bot import get_tot_pot, comp_hand_equity, decision_algo, comp_is_BB, comp_n_act_players, print_cards, print_state, was_raised, comp_last_amount
import re
from collections import OrderedDict
from torch.nn import functional as F
import random
from utils_io import write_declare_action_state, write_round_start_state, write_round_result_state, find_action_id, find_round_id


my_verbose_upper = False
write_details = False

from networks import Net, Net_2, Net_6maxSingle
    
    
class LSTMBot(BasePokerPlayer):  
    def __init__(self, id_=1, gen_dir='./simul_data/simul_0/gen_0', full_dict = None, network='first', input_type='reg'):
    
        self.network = network
        if full_dict == None:
            i_opp = self.init_i_opp()
            i_gen = self.init_i_gen()
            if self.network =='first':
                self.model = Net(i_opp,i_gen)
            elif self.network =='second':
                self.model=Net_2(i_opp,i_gen)
            elif self.network == '6max_single':
                self.model=Net_6maxSingle(i_gen)
            self.state_dict = next(self.model.modules()).state_dict()   #weights are automaticaly generated
            full_dict_ = self.state_dict.copy()
            full_dict_.update(i_opp), full_dict_.update(i_gen)    
            self.full_dict = full_dict_
        else:
            self.full_dict= full_dict
            self.state_dict, i_opp, i_gen = get_sep_dicts(full_dict)
            if self.network =='first':
                self.model = Net(i_opp,i_gen)
            elif self.network =='second':
                self.model=Net_2(i_opp,i_gen)
            elif self.network == '6max_single':
                self.model=Net_6maxSingle(i_gen)
            self.model.load_state_dict(self.state_dict)
        self.id = id_
        self.gen_dir = gen_dir
        #if not os.path.exists(self.gen_dir+'/bots/'+str(self.id)):
        #    os.makedirs(self.gen_dir+'/bots/'+str(self.id)) 
        self.opponent = None
        self.input_type = input_type
        self.num_players = 6

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        self.new_round_handle(round_state)
        input_tensor = self.prep_input(hole_card, round_state, valid_actions, inputs=self.input_type)
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
        if random.random() < 0.01:
            print('\n LSTM')
            print('net input: ' +str(input_tensor))
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
        self.round_count = round_count
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
        i_opp = OrderedDict()
        if self.network=='first':
            i_opp_keys = ['opp_h0','opp_c0']
            for key in i_opp_keys:
                i_opp[key]=torch.randn(50).view(1,1,50)
        elif self.network=='second':
            i_opp_keys = ['opp_h0_'+str(i) for i in range(10)]+['opp_c0_'+str(i) for i in range(10)]
            for key in i_opp_keys:
                i_opp[key]=torch.randn(10).view(1,1,10)
        #elif self.network=='6maxSingle':
            #i_opp=None
        return i_opp
    
    def init_i_gen(self):
        i_gen_keys = ['gen_h0_'+str(i) for i in range(10)]+['gen_c0_'+str(i) for i in range(10)]
        i_gen = OrderedDict()
        for key in i_gen_keys:
            i_gen[key]=torch.randn(10).view(1,1,10)
        return i_gen
    
    def new_round_handle(self, round_state):
        if round_state['street'] =='preflop' and len([action['action'] for action in round_state['action_histories']['preflop'] if action['uuid']==self.uuid and not(action['action'] in ['BIGBLIND', 'SMALLBLIND'])]) == 0:
            self.model.reset_u_gen()
        return
    
    def prep_input(self, hole_card, round_state, valid_actions, inputs = 'reg'):
        
        if inputs =='reg':
            n_act_players = comp_n_act_players(round_state)
            
            input_size = 8
            
            inputs = [0,]*input_size
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
            call_amount = [action['amount'] for action in valid_actions if action['action']=='call'][0]
            inputs[7] = call_amount/(call_amount+tot_pot)
        
        elif inputs == 'pstratstyle':
            n_act_players = comp_n_act_players(round_state)
            
            input_size = 12
            
            inputs = [0,]*input_size
            #setting street one-hot encoding
            streets =  ['preflop', 'flop', 'turn', 'river']
            street_ind = streets.index(round_state['street'])
            inputs[street_ind] = 1
            
            #nb opponent players
            inputs[4] = (n_act_players-1)/self.num_players
            
            #setting position at table
            BB_pos = round_state['small_blind_pos']-1
            players_after_hero = (BB_pos-round_state['next_player'])%self.num_players
            players_between_pos = [(BB_pos - diff)%self.num_players for diff in range(0,players_after_hero)]
            #print('players between: '+str(len(players_between_pos)))
            nb_folded_between = len([player_pos for player_pos in players_between_pos if round_state['seats'][player_pos]['state'] != 'participating'])
            #print('nb_folded: '+str(nb_folded_between))
            players_participating_after_hero = (round_state['small_blind_pos']-1-nb_folded_between-round_state['next_player'])%self.num_players
            inputs[5] = players_participating_after_hero/self.num_players
            
            #setting hand equity
            inputs[6] = comp_hand_equity(hole_card = hole_card, community_card = round_state['community_card'], n_act_players = n_act_players)
            
            ##setting my equity on flop
            nb_flop_cards = 3
            if street_ind<=1:
                inputs[7] = comp_hand_equity(hole_card = hole_card, community_card = round_state['community_card'], n_act_players = n_act_players, nb_board_cards = nb_flop_cards)
            else: #if on turn or river
                inputs[7]=0
            ## wether the street is raised
            #inputs[9] = 1*was_raised(round_state)
            
            ## my current stack
            inputs[8] = round_state['seats'][round_state['next_player']]['stack']/self.i_stack

            # call amount
            call_amount = [action['amount'] for action in valid_actions if action['action']=='call'][0]
            my_last_amount= comp_last_amount(round_state=round_state, my_uuid=self.uuid)
            call_price = call_amount-my_last_amount
            inputs[9] = call_price/self.i_stack
            
            # total pot
            tot_pot = get_tot_pot(round_state['pot'])
            inputs[10] = tot_pot/self.i_stack
            
            #big blind level
            inputs[11] = 2*round_state['small_blind_amount']/self.i_stack
            
            
            #print(inputs)
            

        return torch.Tensor(inputs).view(1, 1, -1)
 
    
    def clear_log(self):
        for logtype in ['declare_action_state','round_start_state','round_result_state']:
            if self.gen_dir != None and os.path.exists(self.gen_dir+'/bots/'+str(self.id)+'/'+str(self.opponent)+'_'+logtype+'.csv'):
                os.remove(self.gen_dir+'/bots/'+str(self.id)+'/'+str(self.opponent)+'_'+logtype+'.csv')
            
    def net_predict(self, input_tensor):
        net_output = self.model(input_tensor)
        return net_output.squeeze().item()
    
    def define_position(self, round_state, player_id):
        rel_pos = (player_id-round_state['small_blind_pos'])%self.num_players
        if (rel_pos<=1):
            pos_group = 'blinds'
        elif (rel_pos>=self.num_players-2):
            pos_group = 'late'
        elif (rel_pos>=self.num_players-5):
            pos_group = 'middle'
        else:
            pos_group = 'early'
        return pos_group

    
def get_sep_dicts(full_dict):
    state_dict = OrderedDict()
    i_opp = OrderedDict()
    i_gen = OrderedDict()
    for layer in sorted(full_dict.keys()):
        pattern_opp = re.compile('opp_')
        pattern_gen = re.compile('gen_')
        if pattern_opp.match(layer):
            i_opp[layer] = full_dict[layer]
        elif pattern_gen.match(layer): 
            i_gen[layer] = full_dict[layer]
        else: 
            state_dict[layer] = full_dict[layer]
    return state_dict, i_opp, i_gen
    
    
def setup_ai():
    return LSTMBot()