#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 14:37:11 2019

@author: cyril
"""



import sys
sys.path.append("..")
import time



##### OMPEVAL #####
print("## OMPEVAL ##")
# Import ctypes, it is native to python
import numpy.ctypeslib as ctl
import ctypes
libname = 'libhandequity.so'
# The path may have to be changed
libdir = '../OMPEval-fork/lib/'
lib = ctl.load_library(libname, libdir)

# Defining the python function from the library
omp_hand_equity = lib.hand_equity
# Determining its arguments and return types
omp_hand_equity.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool]
omp_hand_equity.restype = ctypes.c_double
# Defining the arguments
hole_card = "9sKs"  # 9 of spades and ten of spades
community_card = "8dAhKh" # Number of cards defined here may very between 0 and 5
nb_players = 6 # Number of players may vary between 2 and 6
nb_board_cards = 3 # Default is 5. If = 3, showdown is at flop
std_err_tol = 10**-3 # Default is 10**-5. This is the std in % at which the hand equity will be returned
verbose = True # Default is False
time_1 = time.time()
# Calling the function (goes from python to C++ and back)
hand_equity = omp_hand_equity(hole_card.encode(), community_card.encode(), nb_players, nb_board_cards, std_err_tol, verbose)
print ("The equity is: " + str(hand_equity*100)+"%")
time_2 = time.time()
print("The total time taken is: "+ str((time_2-time_1)*1000)+ " [ms]")
#print(results)


##### DEUCES #####
print("## DEUCES ##")
from deuces.card import Card
from deuces.evaluator import Evaluator
from deuces.deck import Deck

def deuces_estimate_win_rate(nb_simulation, nb_player, hole_card, board):

    # Estimate the win count by doing a Monte Carlo simulation
    win_count = sum([deuces_montecarlo_simulation(nb_player, hole_card, board) for _ in range(nb_simulation)])
    return 1.0 * win_count / nb_simulation


def deuces_montecarlo_simulation(nb_player, hole_card, board):
    deck = Deck()
    for card in hole_card+board:
        deck.remove_card(card)
    board_full = board + deck.draw(5-len(board))
    opponents_hole = [deck.draw(2) for i in range(nb_player - 1)]#[unused_cards[2 * i:2 * i + 2] 
    opponents_score = [evaluator.evaluate(board_full, hole) for hole in opponents_hole]#[HandEvaluator.eval_hand(hole, community_card) for hole in opponents_hole]
    my_score = evaluator.evaluate(board_full, hole_card)#HandEvaluator.eval_hand(hole_card, community_card)
    return 1 if my_score < min(opponents_score) else 0


evaluator = Evaluator()
hole_card = [Card.new('9s'),Card.new('Ks')]
board = [Card.new('8d'),Card.new('Ah'),Card.new('Kh')]
nb_players = 6
nb_simulations = 10000

time_1 = time.time()
hand_equity = deuces_estimate_win_rate(nb_simulations,nb_players,hole_card, board)
print ("The equity is: " + str(hand_equity*100)+"%")
time_2 = time.time()
print("The total time taken is: "+ str((time_2-time_1)*1000)+ " [ms]")

### Getting evals/s
evaluator = Evaluator()
hole_card = [Card.new('9s'),Card.new('Ks')]
board_full = [Card.new('8d'),Card.new('Ah'),Card.new('Kh'),Card.new('2s'),Card.new('6h')]
nb_simulations = 100000
time_1 = time.time()
for _ in range (nb_simulations):
    evaluator.evaluate(board_full, hole_card)
time_2 = time.time()
eval_per_sec = nb_simulations / (time_2-time_1)
print("Speed: "+ str(eval_per_sec*10**-3)+" [kEval/s]") 


##### PYPOKERENGINE #####
print('### PYPOKERENGINE ###')
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
      
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
    return 1 if my_score > max(opponents_score) else 0      
      
    
hole_card = ['S9','SK']
board = ['D8','HA','HK']
nb_players = 6
nb_simulations = 10000

time_1 = time.time()
hand_equity = estimate_win_rate(nb_simulations,nb_players,hole_card, board)
print ("The equity is: " + str(hand_equity*100)+"%")
time_2 = time.time()
print("The total time taken is: "+ str((time_2-time_1)*1000)+ " [ms]")

### Getting evals/s
hole_card = ['S9','SK']
board_full = ['D8','HA','HK','S2','H6']
hole_card = gen_cards(hole_card)
board_full = gen_cards(board_full)
nb_simulations = 100000
time_1 = time.time()
for _ in range (nb_simulations):
    HandEvaluator.eval_hand(hole_card, board_full)
time_2 = time.time()
eval_per_sec = nb_simulations / (time_2-time_1)
print("Speed: "+ str(eval_per_sec*10**-3)+" [kEval/s]") 