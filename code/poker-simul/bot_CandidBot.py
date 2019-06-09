#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 15:24:27 2019

@author: cyril
"""


from pypokerengine.players import BasePokerPlayer
from utils_bot import comp_hand_equity, decision_algo, comp_n_act_players, comp_is_BB

my_verbose = False

class CandidBot(BasePokerPlayer): 
    def declare_action(self, valid_actions, hole_card, round_state):
        n_act_players = comp_n_act_players(round_state)
        equity = comp_hand_equity(hole_card = hole_card, community_card = round_state['community_card'], n_act_players = n_act_players)
        o = equity**7
        if o>(2/3):
            print('yay')
        action, amount = decision_algo(net_output=o, round_state=round_state, valid_actions = valid_actions,
                                       i_stack = self.i_stack, my_uuid = self.uuid, verbose = my_verbose)
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
    
def setup_ai():
    return CandidBot()
