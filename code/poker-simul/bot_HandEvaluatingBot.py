#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 17:19:30 2019

@author: cyril
"""

from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
from tools import flatten_list
from functools import reduce
# Import ctypes, it is native to python
import numpy.ctypeslib as ctl
import ctypes

my_verbose = False

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
verbose = False # Default is False


def format_cards(cards):
    if cards != []:
        formatted_cards =  reduce((lambda x1,x2: x1+x2), [card[1]+card[0].lower() for card in cards])
    else:
        formatted_cards = ""
    return formatted_cards

class HandEvaluatingBot(BasePokerPlayer):
    def __init__(self):
        super().__init__()
        self.wins = 0
        self.losses = 0

    def declare_action(self, valid_actions, hole_card, round_state):
        self.num_active_players = sum([player['state']=='participating' for player in round_state['seats']])
        # Estimate the win rate
        win_rate = omp_hand_equity(format_cards(hole_card).encode(), format_cards(round_state['community_card']).encode(), 
                                     self.num_active_players, nb_board_cards, std_err_tol, verbose)
        
        if(my_verbose):    
            print("My cards are: "+ str(hole_card))
            print("My win rate is of: "+str(win_rate)+ "% with num_active_players: " +str(self.num_active_players))
            pass
        # Check whether it is possible to call
        can_call = len([item for item in valid_actions if item['action'] == 'call']) > 0
        if can_call:
            # If so, compute the amount that needs to be called
            call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
        else:
            call_amount = 0

        amount = None

        # If the win rate is large enough, then raise / call
        if win_rate > 1/self.num_players:
            raise_amount_options = [item for item in valid_actions if item['action'] == 'raise'][0]['amount']
            if win_rate > 2:#1.8/self.num_players:
                # If it is extremely likely to win, then raise as much as possible
                action = 'raise'
                amount = raise_amount_options['max']
            elif win_rate > 2:# 1.2/self.num_players:
                # If it is likely to win, then raise by the minimum amount possible
                action = 'raise'
                amount = raise_amount_options['min']
            else:
                # If there is a chance to win, then call
                action = 'call'
                amount = call_amount
        else:
            action = 'call' if can_call and call_amount == 0 else 'fold'

        if amount == -1:
            #want to raise but can only call
            action = 'call'
            amount = call_amount

        if amount is None:
            # Set the amount for calling or folding
            items = [item for item in valid_actions if item['action'] == action]
            amount = items[0]['amount']

        if(my_verbose):
            print("Taking action :"+ str(action))
        return action, amount

    def receive_game_start_message(self, game_info):
        self.num_players = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        is_winner = self.uuid in [item['uuid'] for item in winners]
        self.wins += int(is_winner)
        self.losses += int(not is_winner)


def setup_ai():
    return HandEvaluatingBot()
