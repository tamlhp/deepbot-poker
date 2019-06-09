#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 02:16:59 2019

@author: cyril
"""
import os
os.environ["OMP_NUM_THREADS"] = "1" # export OMP_NUM_THREADS=4
os.environ["OPENBLAS_NUM_THREADS"] = "1" # export OPENBLAS_NUM_THREADS=4 
os.environ["MKL_NUM_THREADS"] = "1" # export MKL_NUM_THREADS=6
os.environ["VECLIB_MAXIMUM_THREADS"] = "1" # export VECLIB_MAXIMUM_THREADS=4
os.environ["NUMEXPR_NUM_THREADS"] = "1" # export NUMEXPR_NUM_THREADS=6


import itertools
from pypokerengine.utils.card_utils import gen_cards
import numpy.ctypeslib as ctl
import ctypes
from functools import reduce
import math

def raise_in_limits(amount, valid_actions, verbose=False):
    #if no raise available, calling
    if [item for item in valid_actions if item['action'] == 'raise'][0]['amount']['min']==-1:
        action_in_limits = 'call'
        amount_in_limits = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
    else:
        action_in_limits = 'raise'
        max_raise = [item for item in valid_actions if item['action'] == 'raise'][0]['amount']['max']
        min_raise = [item for item in valid_actions if item['action'] == 'raise'][0]['amount']['min']
        if amount>max_raise:
            if(verbose):
                print('Going all in')
            amount_in_limits = max_raise
        elif amount<min_raise:
            amount_in_limits = min_raise
        else:
            amount_in_limits = amount
    return action_in_limits, amount_in_limits

def fold_in_limits(valid_actions, round_state, my_uuid, verbose = False):
    # Check whether it is possible to call
    #call_exists = len([item for item in valid_actions if item['action'] == 'call']) > 0
    my_last_amount = comp_last_amount(round_state=round_state,my_uuid=my_uuid)
    #if call_exists:
        # If so, compute the amount that needs to be called
    call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
    #else:
    #    call_amount = 0
    #action = 'call' if call_exists and call_amount == 0 else 'fold'
    if call_amount == my_last_amount:
        action='call'
        amount = call_amount
    else:
        action='fold'
        amount=0
    #if (my_verbose):
    #    if action =='call': print('Calling')
    #    elif action == 'fold': print('Folding')
    return action, amount


    

def is_strong_flush_draw(hole_card, round_state, my_verbose=False):
    color_list = [card.suit for card in hole_card+gen_cards(round_state['community_card'])]
    #color_list = []
    color_match = [0,]*4
    flush_color = None
    for a, b in itertools.combinations(color_list, 2):
        if (a==b):
            for i in range(4):
                if(a==2**(i+1)):
                    color_match[i]+=1
    for i in range(4):
        if color_match[i]>=6:
            flush_color = 2**(i+1)
    #there is a flush draw (of 4 cards)
    if ((flush_color != None)
    #hole cards are suited (and in flush draw)
    and ((hole_card[0].suit == hole_card[1].suit and hole_card[0].suit == flush_color)
    #hole card in flush draw is A or K
    or any([hole_card[j].rank in ['A','K'] for j in range(2)]))):
        if True:
            print('Strong flush draw')
            print_cards(hole_card = hole_card, round_state=round_state)
        return True
    else:
        return False

def is_strong_straight_draw(hole_card, round_state, my_verbose = False):
    #define list of ranks of available cards
    rank_list = [card.rank for card in hole_card + gen_cards(round_state['community_card'])]
    #keep unique elements
    rank_list = list(set(rank_list))
    #removing ace as it never gives open-ended straights
    if(14 in rank_list): rank_list.remove(14)#rank_list.append(1)
    nb_neighbors = {}
    cards_with_two_neighbors = []
    for a, b in itertools.combinations(rank_list, 2):
        if (a not in nb_neighbors.keys()): nb_neighbors[a]=0
        if (b not in nb_neighbors.keys()): nb_neighbors[b]=0

        if(abs(a-b) == 1):
            nb_neighbors[a]+=1
            nb_neighbors[b]+=1
     #at least 2 cards have 2 neighbors
    if sum([x==2 for x in nb_neighbors.values()])>=2:
        cards_with_two_neighbors = [d for d, s in zip(nb_neighbors.keys(), [x==2 for x in nb_neighbors.values()]) if s]
        if(abs(cards_with_two_neighbors[0]-cards_with_two_neighbors[1])==1):
            if(True):
                print('Strong straight draw')
                print_cards(hole_card = hole_card, round_state=round_state)
            return True
    return False

def was_raised(round_state):
        return any([action_desc['action']=='RAISE' for action_desc in round_state['action_histories'][round_state['street']]])

def was_raised_twice(round_state):
        return sum([action_desc['action']=='RAISE' for action_desc in round_state['action_histories'][round_state['street']]])>=2

def print_cards(hole_card, round_state):
    print('Hole cards: ' + str(list(map(lambda x: x.__str__(), hole_card)))
        + ', community cards: ' +str(list(map(lambda x: x.__str__(), gen_cards(round_state['community_card'])))))

def print_state(net_output,action,amount):
    print('net output: %.2f action: %s, amount: %i' % (net_output, action, amount))


def get_tot_pot(pot):
    tot_pot = [pot[key]['amount'] for key in pot.keys() if key == 'main'][0]
    if len(pot.keys())>=1:
        for i in range(len(pot['side'])):
            tot_pot += pot['side'][i]['amount']
    return tot_pot


def format_cards(cards):
    if cards != []:
        formatted_cards =  reduce((lambda x1,x2: x1+x2), [card[1]+card[0].lower() for card in cards])
    else:
        formatted_cards = ""
    return formatted_cards


def comp_hand_equity(hole_card, community_card, n_act_players, nb_board_river = 5, std_err_tol = 1**-3, verbose = False):
    # nb_board_cards : Default is 5. If = 3, showdown is at flop
    # std_err_tol : Default is 10**-5 (in c++). This is the std in % at which the hand equity will be returned
    libname = 'libhandequity.so'
    # The path may have to be changed
    libdir = '../OMPEval_fork/lib/'
    lib = ctl.load_library(libname, libdir)
    # Defining the python function from the library
    omp_hand_equity = lib.hand_equity
    # Determining its arguments and return types
    omp_hand_equity.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_bool]
    omp_hand_equity.restype = ctypes.c_double

    
    hand_equity = omp_hand_equity(format_cards(hole_card).encode(), format_cards(community_card).encode(), 
                                     n_act_players, nb_board_river, std_err_tol, verbose)
    
    return hand_equity



def decision_algo(net_output, round_state, valid_actions, i_stack, my_uuid, verbose=False):    
    #pot = round_state['pot']
    BB = 2*round_state['small_blind_amount']
    #is_BB= comp_is_BB(round_state, my_uuid)
    my_last_amount = comp_last_amount(round_state=round_state,my_uuid=my_uuid)
    y = net_output*i_stack + my_last_amount
    
    tot_pot = get_tot_pot(pot=round_state['pot'])
    call_amount = [action['amount'] for action in valid_actions if action['action']=='call'][0] 
    min_raise = [action['amount']['min'] for action in valid_actions if action['action']=='raise'][0]

    if min_raise == -1:
        min_raise = math.inf
    #print(y)
    street_was_raised_twice =was_raised_twice(round_state=round_state)
    if y<call_amount:
        action, amount = fold_in_limits(valid_actions=valid_actions, round_state = round_state, my_uuid = my_uuid, verbose= False)
    elif y< min_raise or (street_was_raised_twice and y<(2/3)*i_stack):#max(call_amount+ (1/2)*BB, min_raise):
        action = 'call'
        amount= call_amount
    else:
        if y>(2/3)*i_stack:
            action, amount = raise_in_limits(amount=math.inf, valid_actions=valid_actions, verbose=verbose)
        else:
            action, amount = raise_in_limits(amount=BB*round(y/BB), valid_actions=valid_actions, verbose=verbose)

        #alternative, only multiples of 0.5*pot
        #action, amount = raise_in_limits(call_amount+ 0.5*tot_pot*round((y-call_price)/(0.5*tot_pot)), valid_actions, verbose)
    """
    # if wanting to raise by more than 2x tot_pot: go all in
    max_raise = [action['amount']['max'] for action in valid_actions if action['action']=='raise'][0]
    if amount >= call_price + 2.5*tot_pot:
        print(y)
        print(amount)
        action, amount = raise_in_limits(max_raise, valid_actions,verbose)
    """
    return action, amount

def comp_last_amount(round_state, my_uuid):
    my_street_amounts = [action['amount'] for action in round_state['action_histories'][round_state['street']] if action['uuid']==my_uuid]
    if len(my_street_amounts)==0:
        last_amount = 0
    else:
        last_amount = max(my_street_amounts)
    return last_amount
    

    
def comp_is_BB(round_state, my_uuid):
    is_BB = len([action for action in round_state['action_histories']['preflop'] if action['uuid']==my_uuid and action['action'] == 'BIGBLIND'])>0
    return is_BB

def comp_n_act_players(round_state):
    n_act_players = sum([player['state'] in ['allin','participating'] for player in round_state['seats']])
    return n_act_players
