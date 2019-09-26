#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 24 23:57:43 2019

@author: cyril
"""
import sys
#sys.path.append('../neural-net')
sys.path.append('../PyPokerEngine')
from pypokerengine.players import BasePokerPlayer
import torch
from torch import nn
import os
from utils_bot import get_tot_pot, comp_hand_equity, decision_algo, comp_is_BB, comp_n_act_players, print_cards, print_state, was_raised, comp_last_amount,comp_last_amount_opp
import re
from collections import OrderedDict
from torch.nn import functional as F
import random
from utils_io import write_declare_action_state, write_round_start_state, write_round_result_state, find_action_id, find_round_id
import pickle

my_verbose_upper = False

from networks import Net, Net_2, Net_6maxSingle, Net_6maxFull

def reduce_full_dict(full_dict):
    nb_opps=4
    nb_LSTM = 10
    for opp_id in range(1,nb_opps+1):
        for lstm_id in range(nb_LSTM):
            full_dict.pop('opp_round_h0_'+str(opp_id)+'_'+str(lstm_id),None)
            full_dict.pop('opp_round_c0_'+str(opp_id)+'_'+str(lstm_id),None)
            full_dict.pop('opp_game_h0_'+str(opp_id)+'_'+str(lstm_id),None)
            full_dict.pop('opp_game_c0_'+str(opp_id)+'_'+str(lstm_id),None)
    return full_dict

def extend_full_dict(full_dict):
    nb_opps=4
    nb_LSTM = 10
    for opp_id in range(1,nb_opps+1):
        for lstm_id in range(nb_LSTM):
            full_dict['opp_round_h0_'+str(opp_id)+'_'+str(lstm_id)] = full_dict['opp_round_h0_0_'+str(lstm_id)].clone()
            full_dict['opp_round_c0_'+str(opp_id)+'_'+str(lstm_id)] = full_dict['opp_round_c0_0_'+str(lstm_id)].clone()
            full_dict['opp_game_h0_'+str(opp_id)+'_'+str(lstm_id)] = full_dict['opp_game_h0_0_'+str(lstm_id)].clone()
            full_dict['opp_game_c0_'+str(opp_id)+'_'+str(lstm_id)] = full_dict['opp_game_c0_0_'+str(lstm_id)].clone()
    return full_dict

class LSTMBot(BasePokerPlayer):
    def __init__(self, id_=1, gen_dir='./simul_data/simul_0/gen_0', full_dict = None, network='first', validation_mode=None, validation_id=None, write_details=False):

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
            elif self.network == '6max_full':
                self.model=Net_6maxFull(i_opp,i_gen)
            self.state_dict = next(self.model.modules()).state_dict()   #weights are automaticaly generated
            full_dict_ = self.state_dict.copy()
            full_dict_.update(i_opp), full_dict_.update(i_gen)
            if self.network == '6max_full':
                full_dict_=reduce_full_dict(full_dict_)
            self.full_dict = full_dict_
        else:
            #print(full_dict['opp_game_h0_0_0'])
            self.full_dict= full_dict
            if self.network == '6max_full':
                full_dict = extend_full_dict(full_dict)
            self.state_dict, i_opp, i_gen = get_sep_dicts(full_dict, network=self.network)
            if self.network =='first':
                self.model = Net(i_opp,i_gen)
            elif self.network =='second':
                self.model=Net_2(i_opp,i_gen)
            elif self.network == '6max_single':
                self.model=Net_6maxSingle(i_gen)
            elif self.network == '6max_full':
                self.model=Net_6maxFull(i_opp,i_gen)
            self.model.load_state_dict(self.state_dict)
        self.id = id_
        self.gen_dir = gen_dir
        #if not os.path.exists(self.gen_dir+'/bots/'+str(self.id)):
        #    os.makedirs(self.gen_dir+'/bots/'+str(self.id)
        self.num_players = 6
        self.validation_mode = validation_mode
        self.validation_id = validation_id
        self.round_count=0
        self.action_id=1
        self.write_details = write_details


    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        #self.stack=round_state['seats'][round_state['next_player']]['stack']
        #print(self.stack)
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        if self.network == '6max_full':
            for key in round_state['action_histories'].keys():
                round_state['action_histories'][key] = [action for action in round_state['action_histories'][key] if action['action']!='ANTE']
        self.new_round_handle(round_state)
        input_tensor = self.prep_input(hole_card, round_state, valid_actions, network=self.network)
        #print('input tensor: '+str(input_tensor))
        net_output = self.net_predict(input_tensor)
        #print('net output: ' +str(net_output))
        version='default'
        if self.network=='6max_full':
            version='newer'
        action, amount = decision_algo(net_output=net_output, round_state=round_state, valid_actions = valid_actions,
                                       i_stack = self.i_stack, my_uuid = self.uuid, verbose = my_verbose_upper, version=version)

        if self.write_details:
            write_declare_action_state(round_id = self.round_count, action_id = self.action_id, net_input=input_tensor, net_output=net_output, action=action, amount = amount,
                               csv_file = self.gen_dir+'/analysis_data/'+str(self.id)+'/declare_action_state.csv')
            self.action_id+=1
        if self.validation_mode == "mutation_variance":
            with open(self.gen_dir+'/outputs_'+str(self.validation_id)+'.pkl', 'ab') as f:
                pickle.dump(net_output, f, protocol=0)
            action, amount = 'fold',0
        if self.validation_mode=="crossover_variance":
            with open(self.gen_dir+'/outputs_'+str(self.validation_id)+'.pkl', 'ab') as f:
                pickle.dump(net_output, f, protocol=0)
            action, amount = 'fold',0
        #if self.validation_mode=='game':
        #    with open(self.gen_dir+'/outputs_'+str(self.validation_id)+'.pkl', 'ab') as f:
        #        pickle.dump(net_output, f, protocol=0)


        if  len(round_state['community_card'])!=0:#random.random() < 0: #net_output>0:##
            print('\n LSTM')
            #print('net input: ' +str(input_tensor))
            print('at round: ' +str(self.round_count))
            print('Stack: ' +str(round_state['seats'][round_state['next_player']]['stack']))
            print('at blind: '+str(round_state['small_blind_amount']))
            print_cards(hole_card = hole_card, round_state=round_state)
            print_state(net_output=net_output, action=action, amount=amount)

        return action, amount   # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        self.i_stack = game_info['rule']['initial_stack']

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.round_count = round_count

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        if self.write_details and False:
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

    def new_round_handle(self, round_state):
        if round_state['street'] =='preflop' and len([action['action'] for action in round_state['action_histories']['preflop'] if action['uuid']==self.uuid and not(action['action'] in ['BIGBLIND', 'SMALLBLIND'])]) == 0:
            self.model.reset_u_gen()
        return

    def prep_input(self, hole_card, round_state, valid_actions, network = 'first'):

        if network =='first' or  network=='second':
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
            #inputs[7] = call_price/(call_price+tot_pot) #VERIFY WHICH WAS USED
            inputs[7] = call_amount/(call_amount+tot_pot)

        elif network.split('_')[0] == '6max':
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
            if len(network.split('_'))>1:
                if True:
                    #NEW VERSION#
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

                else:
                #OLD VERSION#
                    if network.split('_')[1] == 'full':
                        nb_opps=5
                        nb_feats=5
                        opp_ids = [1,2,3,4,5,6]
                        opp_ids.remove(int(self.uuid.split('-')[1]))
                        opp_input_size=nb_opps*nb_feats
                        opp_inputs=[0,]*opp_input_size
                        nb_folded_since=0
                        for i in range(nb_opps):
                            opp_last_amount= comp_last_amount_opp(round_state=round_state,my_uuid='uuid-'+str(opp_ids[i]))
                            for player in round_state['seats']:
                                if player['name']=='p-'+str(opp_ids[i]):
                                    #setting active / unactive bit
                                    opp_inputs[0+i*nb_feats]= not(player['state']=='folded')*1
                                    ###opponents stack
                                    opp_inputs[1+i*nb_feats]=player['stack']/self.i_stack
                                    break

                            for k, action in enumerate(round_state['action_histories'][round_state['street']][::-1]):
                                if action['uuid']==self.uuid:
                                    break
                                elif action['uuid']=='uuid-'+str(opp_ids[i]):
                                    street_amount = max([action['amount'] for action in round_state['action_histories'][round_state['street']][::-1][(k+1):] if action['action']!='FOLD']+[0])
                                    if action['action']=='FOLD':
                                        amount=0
                                    else:
                                        amount=action['amount']
                                    #opponents paid amount
                                    opp_inputs[2+i*nb_feats]=(amount-opp_last_amount)/self.i_stack
                                    #opponents faced call price
                                    opp_inputs[3+i*nb_feats]=(street_amount-opp_last_amount)/self.i_stack
                                    nb_folded_since= sum([action['action']=='FOLD' for action in round_state['action_histories'][round_state['street']][::-1][:k+1]])
                                    break
                            #nb opponent players
                            if opp_inputs[0+i*nb_feats]==1:
                                opp_inputs[4+i*nb_feats]= (n_act_players-1+nb_folded_since)/self.num_players
                        inputs=inputs+opp_inputs


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
