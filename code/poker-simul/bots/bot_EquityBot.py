#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 17:19:30 2019

@author: cyril
"""

from pypokerengine.players import BasePokerPlayer
from functools import reduce
from u_bot import raise_in_limits, get_tot_pot, comp_hand_equity, fold_in_limits, comp_last_amount, print_cards, comp_n_act_players
import random

my_local_verbose = False

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
        n_act_players = comp_n_act_players(round_state)
        # Estimate the win rate
        win_rate = comp_hand_equity(hole_card = hole_card, community_card = round_state['community_card'], n_act_players = n_act_players)
        if(my_local_verbose):
            print("My cards are: "+ str(hole_card))
            print("My win rate is of: "+str(win_rate)+ "% with num_active_players: " +str(n_act_players))
            pass

        call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
        my_last_amount = comp_last_amount(round_state=round_state,my_uuid=self.uuid)

        # If the win rate is large enough, then raise / call
        if win_rate > 1/n_act_players:
            tot_pot = get_tot_pot(round_state['pot'])
            min_raise = [action['amount']['min'] for action in valid_actions if action['action']=='raise'][0]
            if win_rate > 1.6/n_act_players:
                # If it is extremely likely to win, then raise by two time the pot
                action = 'raise'
                amount = call_amount+2*tot_pot#raise_amount_options['max']
                action, amount = raise_in_limits(amount=amount, valid_actions=valid_actions,verbose=my_local_verbose)
            elif win_rate > 1.4/n_act_players:
                # If it is very likely to win, then raise by one time the pot
                action = 'raise'
                amount = call_amount+tot_pot#raise_amount_options['max']
                action, amount = raise_in_limits(amount=amount, valid_actions=valid_actions,verbose=my_local_verbose)
            elif win_rate > 1.2/n_act_players:
                # If it is likely to win, then raise by the minimum amount possible
                action = 'raise'
                amount = min_raise
                action, amount = raise_in_limits(amount=amount, valid_actions=valid_actions,verbose=my_local_verbose)
            else:
                # If there is a positive chance to win, then call
                action = 'call'
                amount = call_amount
        else:
            action, amount = fold_in_limits(valid_actions=valid_actions, round_state=round_state, my_uuid=self.uuid)

        if(my_local_verbose):
            print("Taking action :"+ str(action))

        if random.random() < 0:
            print_cards(hole_card = hole_card, round_state=round_state)
            print('action: ' +str(action) + '; amount: ' + str(amount))
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
