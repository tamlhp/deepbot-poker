#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 13:09:35 2019

@author: cyril
"""

from pypokerengine.players import BasePokerPlayer
from utils_bot import was_raised, get_tot_pot

class ManiacBot(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

 
    def declare_action(self, valid_actions, hole_card, round_state):
        action = 'raise'
        tot_pot = get_tot_pot(pot = round_state['pot'])
        call_price = [action['amount'] for action in valid_actions if action['action']=='call'][0]
        if was_raised(round_state):
            amount = call_price + 2*tot_pot
        else:
            amount = call_price + tot_pot
            
            
        return action, amount   # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
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
    return ManiacBot()