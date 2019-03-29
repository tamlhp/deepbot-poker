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

my_verbose = False

# Estimate the ratio of winning games given the current state of the game
def estimate_win_rate(nb_simulation, nb_player, hole_card, community_card=None):
    if not community_card: community_card = []

    # Make lists of Card objects out of the list of cards
    community_card = gen_cards(community_card)
    hole_card = gen_cards(hole_card)

    # Estimate the win count by doing a Monte Carlo simulation
    win_count = sum([montecarlo_simulation(nb_player, hole_card, community_card) for _ in range(nb_simulation)])
    return 1.0 * win_count / nb_simulation


def montecarlo_simulation(nb_player, hole_card, community_card):
    # Do a Monte Carlo simulation given the current state of the game by evaluating the hands
    community_card = _fill_community_card(community_card, used_card=hole_card + community_card)

    unused_cards = _pick_unused_card((nb_player - 1) * 2, hole_card + community_card)
    opponents_hole = [unused_cards[2 * i:2 * i + 2] for i in range(nb_player - 1)]
    opponents_score = [HandEvaluator.eval_hand(hole, community_card) for hole in opponents_hole]
    my_score = HandEvaluator.eval_hand(hole_card, community_card)
    if (my_verbose):
        print("Opponent's scores: "+ str(opponents_score))
        print("My score: "+str(my_score))
        pass
    return 1 if my_score >= max(opponents_score) else 0


def estimate_flop_odd(nb_simulation, nb_player, hole_card, community_card=None):
    if not community_card: community_card = []

    # Make lists of Card objects out of the list of cards
    community_card = gen_cards(community_card)
    hole_card = gen_cards(hole_card)

    # Estimate the win count by doing a Monte Carlo simulation
    win_count = sum([preflop_montecarlo_simulation(nb_player, hole_card, community_card) for _ in range(nb_simulation)])
    return 1.0 * win_count / nb_simulation


def preflop_montecarlo_simulation(nb_player, hole_card, community_card):
    # Do a Monte Carlo simulation given the current state of the game by evaluating the hands
    
    community_card = _fill_community_card(community_card, used_card=hole_card + community_card)
    flop_card = [community_card[i] for i in range(3)]
    unused_cards = _pick_unused_card((nb_player - 1) * 2, hole_card + flop_card)
    opponents_hole = [unused_cards[2 * i:2 * i + 2] for i in range(nb_player - 1)]
    opponents_score = [HandEvaluator.eval_hand(hole, flop_card) for hole in opponents_hole]
    my_score = HandEvaluator.eval_hand(hole_card, flop_card)
    return 1 if my_score >= max(opponents_score) else 0


    """
    # for equity at flop, useless as expectation is same, could be use for std though
    nb_subsimulation = 100
    wins = 0
    for i in range(nb_subsimulation):
        community_card = _fill_community_card(flop_card, used_card=flop_card + hole_card + flatten_list(opponents_hole))
        opponents_score = [HandEvaluator.eval_hand(hole, community_card) for hole in opponents_hole]
        my_score = HandEvaluator.eval_hand(hole_card, community_card)
        if my_score>=max(opponents_score): wins +=1 
    return wins/nb_subsimulation
    """


class HandEvaluatingBot(BasePokerPlayer):
    def __init__(self):
        super().__init__()
        self.wins = 0
        self.losses = 0

    def declare_action(self, valid_actions, hole_card, round_state):
        print(round_state)
        # Estimate the win rate
        win_rate = estimate_win_rate(100, self.num_players, hole_card, round_state['community_card'])
        if(my_verbose):
            print("My cards are: "+ str(hole_card))
            print("My win rate is of: "+str(win_rate)+ "% with num_players: " +str(self.num_players))
            pass
        # Check whether it is possible to call
        can_call = len([item for item in valid_actions if item['action'] == 'call']) > 0
        if can_call:
            # If so, compute the amount that needs to be called
            call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
        else:
            call_amount = 0

        amount = None

        # If the win rate is large enough, then raise
        if win_rate > 1/self.num_players:
            raise_amount_options = [item for item in valid_actions if item['action'] == 'raise'][0]['amount']
            if win_rate > 1.8/self.num_players:
                # If it is extremely likely to win, then raise as much as possible
                action = 'raise'
                amount = raise_amount_options['max']
            elif win_rate > 1.2/self.num_players:
                # If it is likely to win, then raise by the minimum amount possible
                action = 'raise'
                amount = raise_amount_options['min']
            else:
                # If there is a chance to win, then call
                action = 'call'
        else:
            action = 'call' if can_call and call_amount == 0 else 'fold'

        # Set the amount
        if amount is None:
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
