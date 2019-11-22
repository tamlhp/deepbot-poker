#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 15:47:46 2019

@author: cyril
"""

from pypokerengine.players import BasePokerPlayer
import random


class TestBot(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        print(valid_actions)
        action = None
        amount = None               
        raise_amount_options = [item for item in valid_actions if item['action'] == 'raise'][0]['amount']
        if random.random() > 0.5:
            # If it is extremely likely to win, then raise as much as possible
            action = 'call'
            amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']

        else:
                # If it is likely to win, then raise by the minimum amount possible
            action = 'raise'
            amount = raise_amount_options['min']
            
        return action, amount

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
    return TestBot()