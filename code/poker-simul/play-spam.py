#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 14:37:11 2019

@author: cyril
"""

import sys
sys.path.append('../PyPokerEngine_fork')

from pypokerengine.api.game import setup_config, start_poker
from bot_CallBot import  CallBot
from bot_EquityBot import EquityBot
from bot_PStratBot import PStratBot



from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
import time
#import itertools
#import glob_file
#from data_preprocessing import prepare_net_inputs
#from deuces.card import Card
#from deuces.evaluator import Evaluator
#from deuces.deck import Deck
#import math
### binomial distribution ###
from utils_simul import compute_ANE

log_dir = './simul_data'
simul_id = 0 ## simul id
gen_id = 0 ## gen id
gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)

nb_bots = 50
nb_hands = 1
sb_amount = 50

def selection_gen_bots(log_dir, simul_id, gen_id, BB, nb_bots):
    
    ANEs = compute_ANE(gen_dir, BB)
    ord_bot_ids = [el+1 for el in sorted(range(len(ANEs)), key=lambda i:ANEs[i], reverse=True)]

    #surv_bot_ids = ord_bot_ids[:int(surv_perc*nb_bots)]
    
    #prime_perc = 0.15
    surv_perc = 0.3
    #prime_bot_ids = ord_bot_ids[:int(prime_perc*nb_bots)]
    #second_bot_ids = ord_bot_ids[int(prime_perc*nb_bots):int(surv_perc*nb_bots)]
    surv_bot_ids = ord_bot_ids[:int(surv_perc*nb_bots)]
    
    surv_ANEs = [ANEs[i-1] for i in surv_bot_ids]

    print(ANEs)
    print(sum(surv_ANEs)/float(len(surv_ANEs)))
    
    prime_bot_ids = [id_ for id_ in surv_bot_ids if ANEs[id_-1] > sum(surv_ANEs)/float(len(surv_ANEs))]
    second_bot_ids = [id_ for id_ in surv_bot_ids if not(ANEs[id_-1] > sum(surv_ANEs)/float(len(surv_ANEs)))]
    
    print(surv_bot_ids)
    print(prime_bot_ids)

#selection_gen_bots(log_dir, simul_id, gen_id, BB=2*sb_amount, nb_bots = 50)


import multiprocessing as mp
n_cores = mp.cpu_count()
print(n_cores)
"""
hole_card = gen_cards(['SA','S2'])
board_card = gen_cards(['C3','H4','H7'])
hole_card = gen_cards(['SA','S2'])
board_card = gen_cards(['C4','H3','H5'])
val = HandEvaluator.search_straight(hole_card+board_card)
print(bin(val))
"""

"""
from ctypes import cdll
lib = cdll.LoadLibrary('./libfoo.so')

class Foo(object):
    def __init__(self):
        self.obj = lib.Foo_new()

    def bar(self):
        lib.Foo_bar(self.obj)

f = Foo()
f.bar()
"""

"""
import numpy.ctypeslib as ctl
import ctypes

libname = 'libhandequity.so'
libdir = '../hand-evaluators/OMPEval-fork/lib/'
lib=ctl.load_library(libname, libdir)

# Defining the python function from the library
omp_hand_equity = lib.hand_equity
# Determining its arguments types
omp_hand_equity.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
# Determining its return type
omp_hand_equity.restype = ctypes.c_double
# Defining the arguments
hole_card = "9sTs"
community_card = "8dAhKh"
nb_players = 6
# Calling the function (goes from python to C++ and back)
hand_equity = omp_hand_equity(hole_card.encode(), community_card.encode(), nb_players) 
print ("The equity is: " + str(hand_equity))
print(results)
#time_1 = time.time()
time_2 = time.time()
print((time_2-time_1)*1000)
#print(results)
"""


"""
from ctypes import cdll
lib = cdll.LoadLibrary('./libClassEquity.so')
#print(lib)

class MyCClass(object):
    def __init__(self):
        self.obj = lib.ClassEquity_new()

    def estimateHand(self):
        lib.MyCClass_estimateHand(self.obj)

acclass = MyCClass()
acclass.etimateHand()
"""

"""
time_1 = time.time()

for i in range(10000):
    board = deck.draw(5)
Card.print_pretty_cards(board)

time_2 = time.time()
print((time_2-time_1)*1000)
"""

"""

def deuces_estimate_win_rate(nb_simulation, nb_player, hole_card, community_card=None):
    #if not community_card: community_card = []

    # Make lists of Card objects out of the list of cards
    #community_card = gen_cards(community_card)
    #hole_card = gen_cards(hole_card)

    # Estimate the win count by doing a Monte Carlo simulation
    win_count = sum([deuces_montecarlo_simulation(nb_player, hole_card, community_card) for _ in range(nb_simulation)])
    return 1.0 * win_count / nb_simulation


def deuces_montecarlo_simulation(nb_player, hole_card, community_card):
    deck = Deck()
    for card in hole_card:
        deck.remove_card(card)
    # Do a Monte Carlo simulation given the current state of the game by evaluating the hands
    board = deck.draw(5)
    #_fill_community_card(community_card, used_card=hole_card + community_card)
    #hole_card = deck.draw(2)
    #unused_cards = _pick_unused_card((nb_player - 1) * 2, hole_card + community_card)
    opponents_hole = deck.draw(2)#[unused_cards[2 * i:2 * i + 2] for i in range(nb_player - 1)]
    opponents_score = [evaluator.evaluate(board, opponents_hole)]#[HandEvaluator.eval_hand(hole, community_card) for hole in opponents_hole]
    my_score = evaluator.evaluate(board, hole_card)#HandEvaluator.eval_hand(hole_card, community_card)
    #print(max(opponents_score))
    return 1 if my_score >= max(opponents_score) else 0




evaluator = Evaluator()
hand = [Card.new('9h'),Card.new('Ts')]
hand = ['H9', 'ST']

time_1 = time.time()
print(estimate_win_rate(1000,6,hand))
time_2 = time.time()
print((time_2-time_1)*1000)




"""



#print(estimate_win_rate(500,2,['HA', 'SK']))
#print(estimate_win_rate(10000,2,['HA', 'SK']))
"""
print(estimate_flop_odd(1000,2,['HA', 'SK']))
print(estimate_flop_odd(1000,2,['HA', 'SK']))
"""
#HandEvaluator.eval_hand(gen_cards(['H2','S2']),gen_cards(['H3','S3','H7']))







"""    
# Estimate the ratio of winning games given the current state of the game
for i in range(100):
    print(estimate_win_rate(1000,3,['SQ','HJ'],['ST','D2','D9']))
"""


"""
#deep postflop debugging
    
def combi_card(hand_score, id_=0):
    if(id_==0):    
        return int(sum([hand_score & (1<<n) for n in range(12,16)])/(2**12))
    elif(id_==1):
        return int(sum([hand_score & (1<<n) for n in range(8,12)])/(2**8))
    else:
        ##Error
        pass  

Hole_cards = ['DA', 'SJ']
community_cards= ['S5', 'CJ', 'CA']
#Hole_cards =  ['CT', 'HT']
#community_cards = ['D3', 'C5', 'C2']
hole_card = gen_cards(Hole_cards)



### Go through possible cases ###
hand_score = HandEvaluator.eval_hand(hole_card,gen_cards(community_cards))
print("{0:b}".format(hand_score))
#hand is two-pair or better
two_pair_score = (1<<17)
pair_score = (1<<16)
strat='none'
#hand is double pair
if(hand_score & two_pair_score):
    print('test1')
    
    print(combi_card(hand_score, 0))
    print(combi_card(hand_score, 1))
#hole cards used in double pair
    if (all([card.rank in [combi_card(hand_score, i)for i in range(2)] for card in hole_card ])):
        print('test2')
        if (hole_card[0].rank != hole_card[1].rank):
            print('test3')
            strat = 'deep_postflop_raise_raise'
#player has a pair    
if(hand_score &  pair_score):
    print('Test1')
    
    print(combi_card(hand_score, 0))
    print(combi_card(hand_score, 1))
    
    #hole card is used in pair
    if(any([card.rank == combi_card(hand_score, i) for card in hole_card for i in range(2)])):
        print('Test2')
        #pair is top
        if(all([combi_card(hand_score)>=card.rank for card in gen_cards(community_cards)])):
            print('Test3')
            strat = 'deep_postflop_raise_raise'
print(strat)
"""


"""

rank_list = [card.rank for card in gen_cards(['HA','HK'] + ['DQ','DJ','S6','C7'])]
rank_list = list(set(rank_list))
if(14 in rank_list): rank_list.append(1)
nb_neighbors = {}
cards_with_two_neighbors = []
for a, b in itertools.combinations(rank_list, 2):
    if (a not in nb_neighbors.keys()): nb_neighbors[a]=0
    if (b not in nb_neighbors.keys()): nb_neighbors[b]=0  

    if(abs(a-b) == 1):
        nb_neighbors[a]+=1
        nb_neighbors[b]+=1
        
print(nb_neighbors)
 #at least 2 cards have 2 neighbors
if sum([x==2 for x in nb_neighbors.values()])>=2:
    cards_with_two_neighbors = [d for d, s in zip(nb_neighbors.keys(), [x==2 for x in nb_neighbors.values()]) if s]
    print(cards_with_two_neighbors)
    if(abs(cards_with_two_neighbors[0]-cards_with_two_neighbors[1])==1):
        print('yes')
    else:
        print('no')
else:
    print('not')


"""













"""
config = setup_config(max_round=1000, initial_stack=3000, small_blind_amount=5)
config.register_player(name="p1", algorithm=CallBot())
config.register_player(name="p2", algorithm=CallBot())
config.register_player(name="p3", algorithm=CallBot())
config.register_player(name="p4", algorithm=PStratBot())
game_result = start_poker(config, verbose=0)

"""





"""
def poker(hands):
    scores = [(i, score(hand.split())) for i, hand in enumerate(hands)]
    winner = sorted(scores , key=lambda x:x[1])[-1][0]
    return hands[winner]

def score(hand):
    ranks = '23456789TJQKA'
    rcounts = {ranks.find(r): ''.join(hand).count(r) for r, _ in hand}.items()
    score, ranks = zip(*sorted((cnt, rank) for rank, cnt in rcounts)[::-1])
    if len(score) == 5:
        if ranks[0:2] == (12, 3): #adjust if 5 high straight
            ranks = (3, 2, 1, 0, -1)
        straight = ranks[0] - ranks[4] == 4
        flush = len({suit for _, suit in hand}) == 1
        '''no pair, straight, flush, or straight flush'''
        score = ([1, (3,1,1,1)], [(3,1,1,2), (5,)])[flush][straight]
    return score, ranks

poker(['8C TS KC 9H 4S', '7D 2S 5D 3S AC', '8C AD 8D AC 9C', '7C 5H 8D TD KS'])
"""
