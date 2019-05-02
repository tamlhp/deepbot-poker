#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 14:37:11 2019

@author: cyril
"""


from pypokerengine.api.game import setup_config, start_poker
from bot_CallBot import  CallBot
from bot_HandEvaluatingBot import HandEvaluatingBot, estimate_flop_odd, estimate_win_rate
from bot_PStratBot import PStratBot



from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards

import itertools
import glob_file
"""
print(estimate_win_rate(1000,2,['HA', 'SK']))
print(estimate_win_rate(1000,2,['HA', 'SK']))

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
