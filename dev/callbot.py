#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 17:19:48 2019

@author: cyril
"""

from pypokerengine.players import BasePokerPlayer
import numpy as np
#from sklearn.neural_network import MLPRegressor


class CallBot(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_card, round_state):
        actions = [item for item in valid_actions if item['action'] in ['call']]
        return list(np.random.choice(actions).values())

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
    return CallBot()