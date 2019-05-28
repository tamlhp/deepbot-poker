#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 17:19:30 2019

@author: cyril
"""

#from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
#from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
from functools import reduce
from utils_bot import raise_in_limits, get_tot_pot, comp_hand_equity


my_verbose = False

def format_cards(cards):
    if cards != []:
        formatted_cards =  reduce((lambda x1,x2: x1+x2), [card[1]+card[0].lower() for card in cards])
    else:
        formatted_cards = ""
    return formatted_cards

class EquityBot(BasePokerPlayer):
    def __init__(self):
        super().__init__()
        self.wins = 0
        self.losses = 0

    def declare_action(self, valid_actions, hole_card, round_state):
        n_act_players = sum([player['state']=='participating' for player in round_state['seats']])
        # Estimate the win rate
        win_rate = comp_hand_equity(hole_card = hole_card, community_card = round_state['community_card'], n_act_players = n_act_players)
        
        
        if(my_verbose):    
            print("My cards are: "+ str(hole_card))
            print("My win rate is of: "+str(win_rate)+ "% with num_active_players: " +str(n_act_players))
            pass
        # Check whether it is possible to call
        #can_call = len([item for item in valid_actions if item['action'] == 'call']) > 0
        #if can_call:
            # If so, compute the amount that needs to be called
        call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
        #else:
         #   call_amount = 0

        amount = None
        # If the win rate is large enough, then raise / call
        if win_rate > 1/self.num_players:
            tot_pot = get_tot_pot(round_state['pot'])
            #call_price = [action['amount'] for action in valid_actions if action['action']=='call'][0]
            min_raise = [action['amount']['min'] for action in valid_actions if action['action']=='raise'][0]       
            if win_rate > 1.8/self.num_players:
                # If it is extremely likely to win, then raise as much as possible
                action = 'raise'
                amount = min_raise+3*tot_pot#raise_amount_options['max']
                action, amount = raise_in_limits(amount, valid_actions,my_verbose)
            elif win_rate > 1.4/self.num_players:
                # If it is extremely likely to win, then raise as much as possible
                action = 'raise'
                amount = min_raise+tot_pot#raise_amount_options['max']
                action, amount = raise_in_limits(amount, valid_actions, my_verbose)
            elif win_rate > 1.1/self.num_players:
                # If it is likely to win, then raise by the minimum amount possible
                action = 'raise'
                amount = min_raise
                action, amount = raise_in_limits(amount, valid_actions, my_verbose)
            else:
                # If there is a chance to win, then call
                action = 'call'
                amount = call_amount
        elif call_amount == 0:
            action = 'call'
            amount = call_amount
        else:
            action = 'fold'
            amount = 0

        if amount == -1:
            #want to raise but can only call
            action = 'call'
            amount = call_amount
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
    return EquityBot()
