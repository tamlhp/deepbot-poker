#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  1 14:46:28 2019

@author: cyril
"""
import glob_file
import constants
import math
my_verbose = False

def format_screen_info():
        

    """ Formatting hole_card """
    if constants.INV_RANK_MAP[glob_file.cards[0].value]>=constants.INV_RANK_MAP[glob_file.cards[1].value]:
        hole_card = [glob_file.cards[0].color+glob_file.cards[0].value, glob_file.cards[1].color+glob_file.cards[1].value]
    else:
        hole_card = [glob_file.cards[1].color+glob_file.cards[1].value, glob_file.cards[0].color+glob_file.cards[0].value]
    """NEW ROUND"""
    if glob_file.hole_card!=hole_card:
        glob_file.round_state = {'action_histories':{'preflop':[], 'flop':[], 'turn':[], 'river':[]}, 'community_card': [], 'pot':{'main':{}}, 'street': '', 'seats':[], 'small_blind_pos':-1, 'big_blind_pos':-1, 'round_count':glob_file.round_count }
        glob_file.round_state['dealer_btn']  = glob_file.dealer_button.at_player
        glob_file.round_state['small_blind_pos'] = (glob_file.dealer_button.at_player+1)%constants.NB_PLAYERS
        glob_file.round_state['big_blind_pos'] = (glob_file.dealer_button.at_player+2)%constants.NB_PLAYERS
        glob_file.hole_card = hole_card
        glob_file.previous_street = None
        glob_file.round_count+=1
        
        for player in glob_file.players[glob_file.round_state['small_blind_pos']:]+ glob_file.players[:glob_file.round_state['small_blind_pos']]:
            player.is_folded = False
            if player.id == glob_file.round_state['big_blind_pos']:
                #setting small blind amount
                glob_file.round_state['small_blind_amount']=int(player.bet_value/2)
                #writing small blind 'bet'
                glob_file.round_state['action_histories']['preflop'].append({'uuid':'uuid'+str((player.id-1)%len(glob_file.players)), 'action': 'SMALLBLIND', 'amount': glob_file.round_state['small_blind_amount'], 'add_amount':glob_file.round_state['small_blind_amount'], 'paid':glob_file.round_state['small_blind_amount']})
                glob_file.players[(player.id-1)%len(glob_file.players)].last_bet_seen = glob_file.round_state['small_blind_amount']
                #writing big blind 'bet'
                glob_file.round_state['action_histories']['preflop'].append({'uuid':'uuid'+str(player.id), 'action': 'BIGBLIND', 'amount': 2*glob_file.round_state['small_blind_amount'], 'add_amount':glob_file.round_state['small_blind_amount'], 'paid':2*glob_file.round_state['small_blind_amount']})
                player.last_bet_seen = 2*glob_file.round_state['small_blind_amount']
            else:
                player.last_bet_seen = 0
                
        glob_file.street_price = 2*glob_file.round_state['small_blind_amount']
        glob_file.previous_bet_value = 2*glob_file.round_state['small_blind_amount']
        
    if my_verbose:
        print(glob_file.hole_card)

    """ Formatting valid_actions """
    if glob_file.check.is_available:
        call_size = 0
    elif glob_file.call.is_available:
        call_size = glob_file.call.value
    else:
        call_size = None
    max_raise = glob_file.players[0].stack_value
    if glob_file.bet.is_available:
        min_raise = glob_file.bet.value
    elif glob_file.raise_to.is_available:
        min_raise = glob_file.raise_to.value + glob_file.players[0].bet_value
    else:
        #raise not available, must call all-in or fold
        min_raise = -1
        max_raise = -1
    glob_file.valid_actions = [{'action':'fold', 'amount':0}, {'action':'call', 'amount':call_size}, {'action':'raise','amount':{'min':min_raise, 'max':max_raise}}]
    if my_verbose:
        print(glob_file.valid_actions)


    """ Formatting round_state """
    #Finding current street
    if not glob_file.all_cards_found:
        ##not all cards spotted yet
        if len(glob_file.cards) == 2:
            current_street = 'preflop'
        elif len(glob_file.cards) == 5:
            current_street = 'flop'
        elif len(glob_file.cards) == 6:
            current_street = 'turn'
        elif len(glob_file.cards) == 7:
            current_street = 'river'
        else:
            if my_verbose:
                print('[Error] Number of cards read is incorrect')
    else:
        ##all cards were already spotted
        current_street = 'preflop'
        if glob_file.cards[4].is_available:
            current_street = 'flop'
            if glob_file.cards[5].is_available:
                current_street = 'turn'
                if glob_file.cards[6].is_available:
                    current_street = 'river'
                    
    glob_file.round_state['community_card'] = [card.color+card.value for card in glob_file.cards[2:] if card.is_available]
    print('com cards: '+str(glob_file.round_state['community_card']))
    
    glob_file.round_state['street'] = current_street
    
    ##Convention for hero position on websites
    glob_file.round_state['next_player'] = constants.HERO_POSITION

    """NEW STREET"""      
    if glob_file.previous_street!=glob_file.round_state['street']:#glob_file.action_histories[glob_file.round_state['street']] == []:
        for player in glob_file.next_players:
            if player.last_bet_seen<glob_file.street_price and glob_file.previous_street!=None:        
                if player.is_available:
                    #player ended up calling on last street
                    print('Called previously')
                    print(player.id)
                    glob_file.round_state['action_histories'][glob_file.previous_street].append({'uuid':'uuid'+str(player.id), 'action': 'CALL', 'amount': glob_file.street_price, 'add_amount':0, 'paid':glob_file.street_price-player.last_bet_seen})
                else:
                    #player ended up folding on last street
                    print('Folded previously')
                    print(player.id)
                    glob_file.round_state['action_histories'][glob_file.previous_street].append({'uuid':'uuid'+str(player.id), 'action': 'FOLD', 'amount': 0, 'add_amount':0, 'paid':0})
           # elif not(player.is_available) and player.last_bet_seen==glob_file.street_price and glob_file.previous_street!=None:
           #     print('Player folded on this street')
           #     print(player.id)
                #player has folded on this street
           #     glob_file.round_state['action_histories'][glob_file.round_state['street']].append({'uuid':'uuid'+str(player.id), 'action': 'FOLD', 'amount': 0, 'add_amount':0, 'paid':0})
        for player in glob_file.players: player.last_bet_seen = 0
        glob_file.street_price = 0
        glob_file.new_street = True
        
        #initializing 'previous bet value' 
        if glob_file.round_state['street']=='preflop':
            glob_file.previous_bet_value=2*glob_file.round_state['small_blind_amount']
        else:
            glob_file.previous_bet_value = 0


    if my_verbose:
        print([bet.value for bet in glob_file.bet_containers])
    
    #defining main pot
    for bet in glob_file.bet_containers:
        if bet.corresponding_entity == 'POT':
            glob_file.round_state['pot']['main']['amount'] = bet.value
    
    #defining players who have played since last update
    if glob_file.new_street and glob_file.round_state['street']=='preflop':
        cutoff_id = (glob_file.round_state['small_blind_pos']+2)%len(glob_file.players)
        if cutoff_id == glob_file.constants.HERO_POSITION:
            glob_file.previous_players = []
        else:
            glob_file.previous_players = glob_file.players[cutoff_id:]
        glob_file.new_street = False
    elif glob_file.new_street:
        glob_file.previous_players = glob_file.players[glob_file.round_state['small_blind_pos']:]
    else:
        glob_file.previous_players = glob_file.players[1:]
    glob_file.next_players = [player for pl in glob_file.players if (pl not in glob_file.previous_players and pl.id!=0)]

    #Filling info of bets currently on table, to round_state['action_histories']
    for player in glob_file.previous_players:
        print('player: '+str(player.id)+ ' has put '+str(player.bet_value))

        if (not(player.is_folded)):
            if not(player.is_available):
                action='FOLD'
                player.is_folded = True
                glob_file.round_state['action_histories'][glob_file.round_state['street']].append({'uuid':'uuid'+str(player.id), 'action': action, 'amount': 0, 'add_amount':0, 'paid':0})
            else:
                if player.bet_value == glob_file.previous_bet_value:
                    action='CALL'
                elif player.bet_value > glob_file.previous_bet_value:
                    action='RAISE'
                else:
                    print('[Error]: A player supposedly put less chips than previous player')
                glob_file.round_state['action_histories'][glob_file.round_state['street']].append({'uuid':'uuid'+str(player.id), 'action': action, 'amount': player.bet_value, 'add_amount':player.bet_value-glob_file.previous_bet_value, 'paid':player.bet_value-player.last_bet_seen})
                player.last_bet_seen=player.bet_value
                #updating the price to play on the street
                if(player.bet_value>glob_file.street_price):
                    glob_file.street_price = player.bet_value
            
                glob_file.previous_bet_value = player.bet_value
                
                
    #update 'seats' (player infos)
    for i, player in enumerate(glob_file.players):
        glob_file.round_state['seats']=[]
        if player.is_folded:
            state = 'folded'
        else: 
            state = 'participating'
        glob_file.round_state['seats'].append({'state': state, 'name': 'p'+str(player.id), 'uuid': 'uuid'+str(player.id), 'stack': player.stack_value})
        
    
        
    glob_file.previous_street = glob_file.round_state['street']
    if True:
        print(glob_file.round_state['action_histories'])
        print('\n')
        #print(glob_file.round_state)

def write_hero_action(action, amount):
    glob_file.round_state['action_histories'][glob_file.round_state['street']].append({'uuid':'uuid'+str(constants.HERO_POSITION), 'action': action, 'amount': amount+ glob_file.previous_bet_value, 'add_amount':amount, 'paid':amount-glob_file.players[0].last_bet_seen})
    glob_file.previous_bet_value = amount + glob_file.previous_bet_value
    glob_file.players[0].last_seen_bet = amount + glob_file.previous_bet_value