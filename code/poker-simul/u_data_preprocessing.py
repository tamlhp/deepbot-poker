#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 12 19:07:08 2019

@author: cyril
"""

from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
import pandas as pd
import ast

HAND_DATA_FEATURES_CSV = '../../data/hand-data/test_features.csv'
my_verbose = True

def prepare_net_inputs(declare_action_csv = '../../data/hand-data/test_action_declare.csv',
                       round_start_csv = '../../data/hand-data/test_round_start.csv',
                       round_result_csv = '../../data/hand-data/test_round_result.csv'):
    nb_MC_simul = 100
    #declare_action_struct = ['round_id','action_id','hole_card','valid_actions','round_state']
    with open(declare_action_csv, 'r') as hand_data_csv:
        df_action = pd.read_csv(hand_data_csv)

    with open(round_start_csv, 'r') as hand_data_csv:
        df_start = pd.read_csv(hand_data_csv, index_col = 0)

    with open(round_result_csv, 'r') as hand_data_csv:
        df_result = pd.read_csv(hand_data_csv, index_col = 0)

    index = df_action.action_id
    columns = ['hero_BBs', 'at_preflop', 'at_flop', 'at_turn', 'at_river',
               'equity_preflop','equity_flop','equity_turn', 'equity_river',
               'nb_players', 'action_fold', 'action_call', 'action_raise',
               'amount', 'winnings']


    feature_list = []
    for i, df_row in enumerate(df_action.itertuples(index=True, name='ActionPoint')):
        feature_row = {}
        round_state = ast.literal_eval(df_row.round_state)

        feature_row['hero_BBs'] = round_state['seats'][round_state['next_player']]['stack']/(2*round_state['small_blind_amount'])
        current_street = round_state['street']
        streets = ['preflop', 'flop', 'turn', 'river']
        for street in streets:
            if current_street == street: feature_row['at_'+street] = 1
            else: feature_row['at_'+street] = 0

        nb_players = sum([player['state']!='folded' for player in round_state['seats']])
        feature_row['nb_players'] = nb_players

        for street in streets:
            feature_row['equity_'+street] = estimate_win_rate(nb_simulation = nb_MC_simul, nb_player = nb_players,
                      hole_card = ast.literal_eval(df_row.hole_card), community_card = round_state['community_card'], to_street = street)


        #strategies = ['deep_preflop_raise_fold', 'deep_preflop_raise_raise', 'deep_postflop_raise_raise', 'short_shove', 'fold']
        actions = ['fold','call','raise']
        for action in actions:
            if action == df_row.action: feature_row['action_'+action] = 1
            else: feature_row['action_'+action] = 0

        feature_row['amount']= df_row.amount/(2*round_state['small_blind_amount'])

        feature_row['winnings']= (ast.literal_eval(df_result.loc[df_row.round_id].round_state)['seats'][round_state['next_player']]['stack'] \
                               - ast.literal_eval(df_start.loc[df_row.round_id].seats)[round_state['next_player']]['stack']) \
                           /(2*round_state['small_blind_amount'])

        if my_verbose and df_row.action_id%100==0:
            print("At action id: " + str(df_row.action_id))

        feature_list.append(feature_row)

    df_net_features = pd.DataFrame(index=index, columns=columns, data=feature_list)
    df_net_features.to_csv(index_label = 'action_id', path_or_buf = HAND_DATA_FEATURES_CSV)



    return

# Estimate the ratio of winning games given the current state of the game
def estimate_win_rate(nb_simulation, nb_player, hole_card, community_card=None, to_street='river'):
    if not community_card: community_card = []
    # Make lists of Card objects out of the list of cards
    community_card = gen_cards(community_card)
    hole_card = gen_cards(hole_card)

    # Estimate the win count by doing a Monte Carlo simulation
    win_count = sum([montecarlo_simulation(nb_player, hole_card, community_card, to_street) for _ in range(nb_simulation)])
    return 1.0 * win_count / nb_simulation

def montecarlo_simulation(nb_player, hole_card, community_card, to_street='river'):
    # Do a Monte Carlo simulation given the current state of the game by evaluating the hands
    if to_street == 'preflop': nb_com_cards = 0
    elif to_street == 'flop': nb_com_cards = 3
    elif to_street == 'turn': nb_com_cards = 4
    elif to_street =='river': nb_com_cards = 5
    else:
        print('[Error] '+str(to_street) +' is not a valid street name')
        pass

    community_card = _fill_community_card(community_card, used_card=hole_card + community_card)
    community_card = [community_card[i] for i in range(nb_com_cards)]
    unused_cards = _pick_unused_card((nb_player - 1) * 2, hole_card + community_card)

    opponents_hole = [unused_cards[2 * i:2 * i + 2] for i in range(nb_player - 1)]
    opponents_score = [HandEvaluator.eval_hand(hole, community_card) for hole in opponents_hole]
    my_score = HandEvaluator.eval_hand(hole_card, community_card)
    return 1 if my_score >= max(opponents_score) else 0



prepare_net_inputs()


"""
valid_actions = [{'action': 'fold', 'amount': 0}, {'action': 'call', 'amount': 100}, {'action': 'raise', 'amount': {'min': 150, 'max': 10000}}]
hole_card = ['SA','SK']
round_state = {'action_histories':
    {'turn': [{'paid': 0, 'uuid': 'dsitwxjfzukumvtbxangpv', 'action': 'CALL', 'amount': 0},
              {'paid': 0, 'uuid': 'kydxboxhgkqcosfunbpkxs', 'action': 'CALL', 'amount': 0}],
    'preflop': [{'add_amount': 50, 'uuid': 'dsitwxjfzukumvtbxangpv', 'action': 'SMALLBLIND', 'amount': 50},
                {'add_amount': 50, 'uuid': 'kydxboxhgkqcosfunbpkxs', 'action': 'BIGBLIND', 'amount': 100},
                {'action': 'FOLD', 'uuid': 'xkrwhpjormlqgduzvsivsb'},
                {'paid': 100, 'uuid': 'wywinfwqxcrtocydvsszbc', 'action': 'CALL', 'amount': 100},
                {'paid': 50, 'uuid': 'dsitwxjfzukumvtbxangpv', 'action': 'CALL', 'amount': 100},
                {'paid': 0, 'uuid': 'kydxboxhgkqcosfunbpkxs', 'action': 'CALL', 'amount': 100}],
    'flop': [{'paid': 0, 'uuid': 'dsitwxjfzukumvtbxangpv', 'action': 'CALL', 'amount': 0},
             {'paid': 0, 'uuid': 'kydxboxhgkqcosfunbpkxs', 'action': 'CALL', 'amount': 0},
             {'paid': 0, 'uuid': 'wywinfwqxcrtocydvsszbc', 'action': 'CALL', 'amount': 0}]},
    'community_card': ['HA', 'H4', 'H2', 'S7'], 'pot': {'main': {'amount': 300}, 'side': []},
    'street': 'turn', 'dealer_btn': 0, 'next_player': 0, 'small_blind_amount': 50,
    'seats': [{'state': 'participating', 'name': 'p1', 'uuid': 'wywinfwqxcrtocydvsszbc', 'stack': 9900},
              {'state': 'participating', 'name': 'p2', 'uuid': 'dsitwxjfzukumvtbxangpv', 'stack': 9900},
              {'state': 'participating', 'name': 'p3', 'uuid': 'kydxboxhgkqcosfunbpkxs', 'stack': 9900},
              {'state': 'folded', 'name': 'p4', 'uuid': 'xkrwhpjormlqgduzvsivsb', 'stack': 10000}],
    'small_blind_pos': 1, 'big_blind_pos': 2, 'round_count': 1}
"""
