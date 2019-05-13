#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 00:16:37 2019

@author: cyril

{'street': 'showdown', 'action_histories': {'preflop': [{'uuid': 'lsuikzckfjdmldnnjzyxzf', 'action': 'SMALLBLIND', 'add_amount': 50, 'amount': 50}, 
{'uuid': 'wthtwugtngstlolgqzihzn', 'action': 'BIGBLIND', 'add_amount': 50, 'amount': 100}, {'uuid': 'xswhuwzyugyzhmdbjdwqqr', 'action': 'FOLD'}, 
{'uuid': 'ngvydldojrrwemxvoqoyly', 'action': 'FOLD'}, {'uuid': 'buyqkcedtbrtjvxbqbimkj', 'paid': 200, 'action': 'RAISE', 'add_amount': 100, 'amount': 200}, 
{'uuid': 'eenrzyypxeaycaafitqybh', 'action': 'FOLD'}, {'uuid': 'lsuikzckfjdmldnnjzyxzf', 'action': 'FOLD'}, {'uuid': 'wthtwugtngstlolgqzihzn', 'action': 'FOLD'}], 
'flop': []}, 'seats': [{'uuid': 'eenrzyypxeaycaafitqybh', 'state': 'folded', 'name': 'p1', 'stack': 3000}, {'uuid': 'lsuikzckfjdmldnnjzyxzf', 'state': 'folded', 'name': 'p2', 'stack': 2950}, 
{'uuid': 'wthtwugtngstlolgqzihzn', 'state': 'folded', 'name': 'p3', 'stack': 2900}, {'uuid': 'xswhuwzyugyzhmdbjdwqqr', 'state': 'folded', 'name': 'p4', 'stack': 3000}, 
{'uuid': 'ngvydldojrrwemxvoqoyly', 'state': 'folded', 'name': 'p5', 'stack': 3000}, {'uuid': 'buyqkcedtbrtjvxbqbimkj', 'state': 'participating', 'name': 'p6', 'stack': 3150}], 
'community_card': ['S7', 'H7', 'CK', 'DQ', 'D6'], 'round_count': 1, 'dealer_btn': 0, 'next_player': 5, 'big_blind_pos': 2, 'small_blind_pos': 1, 'small_blind_amount': 50, 'pot': 
{'main': {'amount': 350}, 'side': []}}
    

    
{'street': 'showdown', 'action_histories': {'preflop': [{'uuid': 'lsuikzckfjdmldnnjzyxzf', 'action': 'SMALLBLIND', 'add_amount': 50, 'amount': 50}, 
{'uuid': 'wthtwugtngstlolgqzihzn', 'action': 'BIGBLIND', 'add_amount': 50, 'amount': 100}, {'uuid': 'xswhuwzyugyzhmdbjdwqqr', 'action': 'FOLD'}, 
{'uuid': 'ngvydldojrrwemxvoqoyly', 'action': 'FOLD'}, {'uuid': 'buyqkcedtbrtjvxbqbimkj', 'paid': 200, 'action': 'RAISE', 'add_amount': 100, 'amount': 200}, 
{'uuid': 'eenrzyypxeaycaafitqybh', 'action': 'FOLD'}, {'uuid': 'lsuikzckfjdmldnnjzyxzf', 'action': 'FOLD'}, {'uuid': 'wthtwugtngstlolgqzihzn', 'action': 'FOLD'}], 
    'flop': []}, 'seats': [{'uuid': 'eenrzyypxeaycaafitqybh', 'state': 'folded', 'name': 'p1', 'stack': 3000}, {'uuid': 'lsuikzckfjdmldnnjzyxzf', 'state': 'folded', 
    'name': 'p2', 'stack': 2950}, {'uuid': 'wthtwugtngstlolgqzihzn', 'state': 'folded', 'name': 'p3', 'stack': 2900}, {'uuid': 'xswhuwzyugyzhmdbjdwqqr', 'state': 'folded',
    'name': 'p4', 'stack': 3000}, {'uuid': 'ngvydldojrrwemxvoqoyly', 'state': 'folded', 'name': 'p5', 'stack': 3000}, {'uuid': 'buyqkcedtbrtjvxbqbimkj', 'state': 'participating',
    'name': 'p6', 'stack': 3150}], 'community_card': ['S7', 'H7', 'CK', 'DQ', 'D6'], 'round_count': 1, 'dealer_btn': 0, 'next_player': 5, 'big_blind_pos': 2, 'small_blind_pos': 1, 
    'small_blind_amount': 50, 'pot': {'main': {'amount': 350}, 'side': []}}
    
    
    
    
    {'action_histories': {'preflop': [{'amount': 50, 'uuid': 'uinxyhtfxxonswifnohsdj', 'action': 'SMALLBLIND', 'add_amount': 50}, 
    {'amount': 100, 'uuid': 'iakszcvpliyieazaujnhtb', 'action': 'BIGBLIND', 'add_amount': 50}, {'uuid': 'hfyfvqjyvcstzpxwecotxm', 'action': 'FOLD'}, 
    {'uuid': 'enzdmgxuzwidddidgposnr', 'action': 'FOLD'}, {'amount': 200, 'uuid': 'qmjekuckdadtmabhnxokqp', 'action': 'RAISE', 'add_amount': 100, 'paid': 200},
    {'uuid': 'hhbopynwukvrqimknmtopr', 'action': 'FOLD'}, {'uuid': 'uinxyhtfxxonswifnohsdj', 'action': 'FOLD'}, 
    {'amount': 600, 'uuid': 'iakszcvpliyieazaujnhtb', 'action': 'RAISE', 'add_amount': 400, 'paid': 500}, 
    {'amount': 1800, 'uuid': 'qmjekuckdadtmabhnxokqp', 'action': 'RAISE', 'add_amount': 1200, 'paid': 1600}, 
    {'amount': 3000, 'uuid': 'iakszcvpliyieazaujnhtb', 'action': 'RAISE', 'add_amount': 1200, 'paid': 2400}]}, 
    'next_player': 5, 'street': 'preflop', 'small_blind_amount': 50, 'big_blind_pos': 2, 'round_count': 7, 
    'seats': [{'stack': 2850, 'uuid': 'hhbopynwukvrqimknmtopr', 'state': 'folded', 'name': 'p1'}, 
    {'stack': 2800, 'uuid': 'uinxyhtfxxonswifnohsdj', 'state': 'folded', 'name': 'p2'},
    {'stack': 0, 'uuid': 'iakszcvpliyieazaujnhtb', 'state': 'allin', 'name': 'p3'}, 
    {'stack': 2850, 'uuid': 'hfyfvqjyvcstzpxwecotxm', 'state': 'folded', 'name': 'p4'}, 
    {'stack': 2850, 'uuid': 'enzdmgxuzwidddidgposnr', 'state': 'folded', 'name': 'p5'}, 
    {'stack': 1800, 'uuid': 'qmjekuckdadtmabhnxokqp', 'state': 'participating', 'name': 'p6'}], 
    'dealer_btn': 0, 'small_blind_pos': 1, 'pot': {'side': [{'amount': 0, 'eligibles': ['iakszcvpliyieazaujnhtb']}], 
    'main': {'amount': 4850}}, 'community_card': []}