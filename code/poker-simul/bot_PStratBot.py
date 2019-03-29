#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 04:25:39 2019

@author: cyril
"""


from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
my_verbose = True



class PStratBot(BasePokerPlayer):
    def __init__(self):
        super().__init__()
        self.hole_card = ['','']
        self.hole_card_num = ['','']
        self.pos_group = ''
        self.street_was_raised = None

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        move = self.define_move(round_state)
        self.street_was_raised = self.street_was_raised(round_state)
     
        if move == 'raise_all-in':
            action, amount = self.raise_(valid_actions, round_state)
        elif move == 'raise_fold':
            if not(self.street_was_raised):
                 action,amount = self.raise_(valid_actions, round_state)
            else:
                action, amount = self.check_fold(valid_actions)

        elif move == 'fold':
            action, amount = self.check_fold(valid_actions)
            
        return action, amount   # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        #print(game_info)
        self.num_players = game_info['player_num']
        self.big_blind_amount = game_info['rule']['small_blind_amount']*2
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.hole_card = hole_card
        self.hole_card_num = sorted([hole_card[0][1],hole_card[1][1]])
        self.pos_group = ''
        pass

    def receive_street_start_message(self, street, round_state):
        if(street=='preflop'):
            self.pos_group = self.define_position(round_state)
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
    
    
    def define_position(self, round_state):
        rel_pos = (round_state['next_player']-round_state['small_blind_pos'])%self.num_players
        if (rel_pos<=2):
            pos_group = 'blinds'
        elif (rel_pos>=self.num_players-2):
            pos_group = 'late'
        elif (rel_pos>=self.num_players-5):
            pos_group = 'middle'
        else:
            pos_group = 'early'
        return pos_group
    
    def define_move(self, round_state):
        
        if(round_state['street']=='preflop'):
            ### Go through possible cases ###
            #holding AA, KK, QQ or AK
            if(self.hole_card_num[0] in ['A','K','Q'] and self.hole_card_num[0] ==self.hole_card_num[1] 
            or self.hole_card_num == ['A','K']):
                strat = 'raise_all-in'
            #holding AJ
            elif(self.hole_card_num==['J','J']): 
                if self.pos_group in ['early','middle']: strat = 'raise_fold'
                elif self.pos_group in ['blinds','late']: strat = 'raise_all-in'
            #holding TT, 99, 88 or AQ
            elif(self.hole_card_num[0] in ['T','9','8'] and self.hole_card_num[0] ==self.hole_card_num[1]
            or self.hole_card_num == ['A','Q']):
                if self.pos_group in ['early']: strat = 'fold'
                elif self.pos_group in ['middle','blinds','late']: strat = 'raise_fold'
            #holding 77, AJ, AT, KQ or KJ
            elif(self.hole_card_num==['7','7']
            or self.hole_card_num in [['A','J'],['A','T'],['K','Q'],['K','J']]):
                if self.pos_group in ['early','middle','blinds']: strat = 'fold'
                elif self.pos_group in ['late']: strat = 'raise_fold'
            else:
                strat = 'fold'
        
        else: #postflop
            ### Go through possible cases ###
            hand_score = HandEvaluator.eval_hand(gen_cards(self.hole_card+round_state['community_card']))
            
            
        if(my_verbose): print('Chosen move is: '+str(strat))
        return strat
    
    def street_was_raised(self, round_state):
        return any([action_desc['action']=='RAISE' for action_desc in round_state['action_histories'][round_state['street']]])
    
    def street_number_called(self, round_state):
        return sum([action_desc['action']=='CALL' for action_desc in round_state['action_histories'][round_state['street']]])
    
    def preflop_raise(self,valid_actions, round_state):
        street_nb_called = self.street_number_called(round_state) 
        
        if not(self.street_was_raised):
            action = 'raise'
            call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
            amount = (3+street_nb_called)*self.big_blind_amount - call_amount
            print('Raising '+str(amount))
        else:
            action = 'raise'
            amount = 3*[action_desc['amount'] for action_desc in round_state['action_histories'][round_state['street']]][-1]
            print('Raising '+str(amount))
        return action, amount
    
    def check_fold(self, valid_actions):
        # Check whether it is possible to call
        can_call = len([item for item in valid_actions if item['action'] == 'call']) > 0
        if can_call:
            # If so, compute the amount that needs to be called
            call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
        else:
            call_amount = 0
        action = 'call' if can_call and call_amount == 0 else 'fold'
        
        if (my_verbose):
            if action =='call': print('Calling')
            elif action == 'fold': print('Folding')
        return action, call_amount
    
def setup_ai():
    return PStratBot()