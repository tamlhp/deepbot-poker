#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 14:43:26 2019

@author: cyril
"""

from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import argparse


#########################################
# parse input
#########################################
parser = argparse.ArgumentParser(description='Train a conv net to predict state value')

parser.add_argument('--MC-simulations',  type=int, default=100 , help='Number of monte-carlo simulations for equity estimation')
parser.add_argument('--hands-csv',  type=str, default= '../../data/hand-data.csv', help='csv containing hand data')

args = parser.parse_args()

#params
mc_simulations = args.MC_simulations
hand_data = args.hands_csv


##inputs
community_card = round_state['community_card']
win_rate = estimate_hole_card_win_rate(
        nb_simulation=NB_SIMULATION,
        nb_player=self.nb_player,
        hole_card=gen_cards(hole_card),
        community_card=gen_cards(community_card)
)
#equity = 