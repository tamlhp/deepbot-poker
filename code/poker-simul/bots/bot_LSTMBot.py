#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 24 23:57:43 2019

@author: cyril
"""
import sys
sys.path.append('../PyPokerEngine')
import os
import random
import pickle
import torch
import re
from pypokerengine.players import BasePokerPlayer
from u_bot import get_tot_pot, comp_hand_equity, decision_algo, comp_n_act_players, print_cards, print_state, was_raised, comp_last_amount,comp_last_amount_opp
from collections import OrderedDict
from utils_io import write_declare_action_state
from u_formatting import extend_full_dict

from networks import Net_HuFirst, Net_HuSecond, Net_6maxSingle, Net_6maxFull

class LSTMBot(BasePokerPlayer):
    def __init__(self, id_=1, network='6max_full', full_dict = None, validation_mode=None, validation_dir='./simul_data/simul_0/gen_0', validation_id=None):

        self.network = network

        #define i_opp and i_gen
        if full_dict == None:
            #only occurs at first generation
            i_opp = self.init_i_opp()
            i_gen = self.init_i_gen()
        else:
            self.full_dict = extend_full_dict(full_dict=full_dict, network=self.network)
            self.state_dict, i_opp, i_gen = get_sep_dicts(self.full_dict, network=self.network)

        #create the neural network (model)
        if self.network =='hu_first':
            self.model = Net_HuFirst(i_opp,i_gen)
        elif self.network =='hu_second':
            self.model=Net_HuSecond(i_opp,i_gen)
        elif self.network == '6max_single':
            self.model=Net_6maxSingle(i_gen)
        elif self.network == '6max_full':
            self.model=Net_6maxFull(i_opp,i_gen)


        if full_dict == None:
            #define full_dict (state_dict + i_opp + i_gen), it is generated randomly
            self.state_dict = next(self.model.modules()).state_dict()
            self.full_dict = self.state_dict.copy()
            self.full_dict.update(i_opp), self.full_dict.update(i_gen)
            self.full_dict = extend_full_dict(full_dict=self.full_dict, network=self.network)
        else:
            #load state dict into network
            self.model.load_state_dict(self.state_dict)

        self.id = id_
        self.action_id=0
        self.round_count=0

        self.validation_mode = validation_mode
        if self.validation_mode!=None:
            self.validation_dir = validation_dir
            self.validation_id = validation_id


    #  Define the logic to make an action
    def declare_action(self, valid_actions, hole_card, round_state):
        self.new_round_handle(round_state)
        input_tensor = self.prep_input(hole_card, round_state, valid_actions, network=self.network)
        net_output = self.net_predict(input_tensor)
        action, amount = decision_algo(net_output=net_output, round_state=round_state, valid_actions = valid_actions,
                                       i_stack = self.i_stack, my_uuid = self.uuid, verbose = False, version=self.network)

        #validation specific action
        if self.validation_mode == "decision_analysis":
            self.action_id+=1
            write_declare_action_state(round_id = self.round_count, action_id = self.action_id, net_input=input_tensor, net_output=net_output, action=action, amount = amount,
                               csv_file = self.validation_dir+'/analysis_data/'+str(self.id)+'/declare_action_state.csv')
        if self.validation_mode == "mutation_variance":
            with open(self.validation_dir+'/outputs_'+str(self.validation_id)+'.pkl', 'ab') as f:
                pickle.dump(net_output, f, protocol=0)
            action, amount = 'fold',0
        if self.validation_mode=="crossover_variance":
            with open(self.validation_dir+'/outputs_'+str(self.validation_id)+'.pkl', 'ab') as f:
                pickle.dump(net_output, f, protocol=0)
            action, amount = 'fold',0

        #prints information relative to bot's decisions periodically, good for monitoring training
        if  random.random() < 0: #len(round_state['community_card'])!=0:#random.random() < 0: #net_output>0:##
            print('\n LSTM')
            print('at round: ' +str(self.round_count))
            print('Stack: ' +str(round_state['seats'][round_state['next_player']]['stack']))
            print('at blind: '+str(round_state['small_blind_amount']))
            print_cards(hole_card = hole_card, round_state=round_state)
            print_state(net_output=net_output, action=action, amount=amount)

        return action, amount

    def receive_game_start_message(self, game_info):
        self.i_stack = game_info['rule']['initial_stack']

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.round_count = round_count

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

    def prep_input(self, hole_card, round_state, valid_actions, network = 'hu_first'):

        if network =='hu_first' or  network=='hu_second':
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
            my_last_amount= comp_last_amount(round_state=round_state, my_uuid=self.uuid)
            call_price = call_amount-my_last_amount
            inputs[7] = call_amount/(call_amount+tot_pot)

        elif network.split('_')[0] == '6max':
            n_act_players = comp_n_act_players(round_state)
            input_size = 12
            nb_players_6max = 6

            inputs = [0,]*input_size
            #setting street one-hot encoding
            streets =  ['preflop', 'flop', 'turn', 'river']
            street_ind = streets.index(round_state['street'])
            inputs[street_ind] = 1

            #nb opponent players
            inputs[4] = (n_act_players-1)/nb_players_6max

            #setting position at table
            BB_pos = round_state['small_blind_pos']-1
            players_after_hero = (BB_pos-round_state['next_player'])%nb_players_6max
            players_between_pos = [(BB_pos - diff)%nb_players_6max for diff in range(0,players_after_hero)]
            #print('players between: '+str(len(players_between_pos)))
            nb_folded_between = len([player_pos for player_pos in players_between_pos if round_state['seats'][player_pos]['state'] != 'participating'])
            #print('nb_folded: '+str(nb_folded_between))
            players_participating_after_hero = (round_state['small_blind_pos']-1-nb_folded_between-round_state['next_player'])%nb_players_6max
            inputs[5] = players_participating_after_hero/nb_players_6max

            #setting hand equity
            if len(network.split('_'))>1:
                if network.split('_')[1] == 'full':
                    inputs[6] = n_act_players*comp_hand_equity(hole_card = hole_card, community_card = round_state['community_card'], n_act_players = n_act_players)
                elif network.split('_')[1] == 'single':
                    inputs[6] = comp_hand_equity(hole_card = hole_card, community_card = round_state['community_card'], n_act_players = n_act_players)


            ##setting my equity on flop
            nb_flop_cards = 3
            if street_ind<=1:
                if len(network.split('_'))>1:
                    if network.split('_')[1] == 'full':
                        inputs[7] = n_act_players*comp_hand_equity(hole_card = hole_card, community_card = round_state['community_card'], n_act_players = n_act_players, nb_board_cards = nb_flop_cards)
                    elif network.split('_')[1] == 'single':
                        inputs[7] = comp_hand_equity(hole_card = hole_card, community_card = round_state['community_card'], n_act_players = n_act_players, nb_board_cards = nb_flop_cards)

            else: #if on turn or river
                inputs[7]=0

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


            ##preparer opponent modelling inputs
            if len(network.split('_'))>1:
                if network.split('_')[1] == 'full':
                    nb_opps=5
                    nb_feats=5
                    opp_ids = [1,2,3,4,5,6]
                    opp_ids.remove(int(self.uuid.split('-')[1]))
                    opp_input_size=nb_opps*nb_feats
                    opp_inputs=[0,]*opp_input_size
                    for i in range(nb_opps):
                        opp_last_amount= comp_last_amount_opp(round_state=round_state,my_uuid='uuid-'+str(opp_ids[i]))
                        for player in round_state['seats']:
                            if player['name']=='p-'+str(opp_ids[i]):
                                #setting active / unactive bit
                                opp_inputs[0+i*nb_feats]= not(player['state']=='folded')*1
                                break

                        for k, action in enumerate(round_state['action_histories'][round_state['street']][::-1]):
                            if action['uuid']==self.uuid:
                                break
                            elif action['uuid']=='uuid-'+str(opp_ids[i]):
                                if action['action']=='FOLD':
                                    amount=0
                                else:
                                    amount=action['amount']
                                #opponents paid amount
                                if action['action'] not in ['SMALLBLIND','BIGBLIND']:
                                    opp_inputs[1+i*nb_feats]=(amount-opp_last_amount)/self.i_stack
                                if action['action']=='RAISE':
                                    opp_inputs[2+i*nb_feats]=1
                                elif action['action']=='CALL':
                                    opp_inputs[3+i*nb_feats]=1
                                elif action['action']=='FOLD':
                                    opp_inputs[4+i*nb_feats]=1
                                break
                    inputs=inputs+opp_inputs


        return torch.Tensor(inputs).view(1, 1, -1)

    def net_predict(self, input_tensor):
        net_output = self.model(input_tensor)
        return net_output.squeeze().item()

    def new_round_handle(self, round_state):
        # reset round relative memory if new round
        if round_state['street'] =='preflop' and len([action['action'] for action in round_state['action_histories']['preflop'] if action['uuid']==self.uuid and not(action['action'] in ['BIGBLIND', 'SMALLBLIND'])]) == 0:
            self.model.reset_u_gen()
        # remove antes for 6max_full
        if self.network == '6max_full':
            for key in round_state['action_histories'].keys():
                round_state['action_histories'][key] = [action for action in round_state['action_histories'][key] if action['action']!='ANTE']
        return

    def init_i_opp(self):
        i_opp = OrderedDict()
        if self.network=='hu_first':
            i_opp_keys = ['opp_h0','opp_c0']
            for key in i_opp_keys:
                i_opp[key]=torch.randn(50).view(1,1,50)
        elif self.network=='hu_second':
            i_opp_keys = ['opp_h0_'+str(i) for i in range(10)]+['opp_c0_'+str(i) for i in range(10)]
            for key in i_opp_keys:
                i_opp[key]=torch.randn(10).view(1,1,10)
        elif self.network=='6max_single':
            pass
        elif self.network=='6max_full':
            i_opp_keys=[]
            for opp_id in range(5):
                i_opp_keys.extend(['opp_round_h0_'+str(opp_id)+'_'+str(i) for i in range(10)]+['opp_round_c0_'+str(opp_id)+'_'+str(i) for i in range(10)])
            for key in i_opp_keys:
                if key.split('_')[3]=='0':
                    i_opp[key]=torch.randn(5).view(1,1,5)
                else:
                    i_opp[key]=i_opp['_'.join(key.split('_')[:3]+['0']+key.split('_')[4:])].clone()
        return i_opp

    def init_i_gen(self):
        i_gen_keys = ['gen_h0_'+str(i) for i in range(10)]+['gen_c0_'+str(i) for i in range(10)]
        i_gen = OrderedDict()
        for key in i_gen_keys:
            i_gen[key]=torch.randn(10).view(1,1,10)
        if self.network=='6max_full':
            i_gen_keys_opp=[]
            for opp_id in range(5):
                i_gen_keys_opp.extend(['opp_game_h0_'+str(opp_id)+'_'+str(i) for i in range(10)]+['opp_game_c0_'+str(opp_id)+'_'+str(i) for i in range(10)])
            for key in i_gen_keys_opp:
                if key.split('_')[3]=='0':
                    i_gen[key]=torch.randn(5).view(1,1,5)
                else:
                    i_gen[key]=i_gen['_'.join(key.split('_')[:3]+['0']+key.split('_')[4:])].clone()
        return i_gen


def get_sep_dicts(full_dict, network=None):
    state_dict = OrderedDict()
    i_opp = OrderedDict()
    i_gen = OrderedDict()
    for layer in sorted(full_dict.keys()):
        if network=='6max_full':
            pattern_opp=re.compile('opp_round')
            pattern_gen=re.compile('gen_|opp_game')
        else:
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
