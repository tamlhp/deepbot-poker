#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 15:47:46 2019

@author: cyril
"""

from pypokerengine.players import BasePokerPlayer


class TestBot(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        print(valid_actions)

        action, amount = self.define_action('deep_preflop_raise',round_state,valid_actions)
        action = 'raise'
        amount = [item for item in valid_actions if item['action'] == 'raise'][0]['amount']['max']
        
        return action, amount   # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
    
    
    def define_action(self, strat, round_state, valid_actions):
        action = None
        amount = None   
        
        if strat == 'deep_preflop_raise_raise':
            street_nb_called = self.number_called(round_state) 
            if not(self.street_was_raised):
                call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
                amount = (3+street_nb_called)*self.big_blind_amount - call_amount
                action, amount = self.raise_in_limits(amount, valid_actions)
            else:
                amount = 3*[action_desc['amount'] for action_desc in round_state['action_histories'][round_state['street']]][-1]
                action, amount = self.raise_in_limits(amount, valid_actions)
                
        elif strat == 'deep_preflop_raise_fold':
            if not(self.street_was_raised):
                action = 'raise'
                call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
                amount = (3+street_nb_called)*self.big_blind_amount - call_amount
            else:
                action, amount = self.check_fold(valid_actions)
        
        elif strat == 'deep_postflop_raise_raise':
            if not(self.street_was_raised):
                call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
                amount = (2/3)*round_state['pot']['main']['amount']
                action, amount = self.raise_in_limits(amount, valid_actions)
            else:
                nb_raise_before = sum([action_desc['action']=='RAISE' for action_desc in round_state['action_histories'][round_state['street']]])
                if nb_raise_before==1:
                    last_raise = [action_desc['action']=='RAISE' for action_desc in round_state['action_histories'][round_state['street']]][-1]['amount']
                    amount = 3*last_raise + round_state['pot']['main']['amount']
                    action, amount = self.raise_in_limits(amount, valid_actions)
                else:
                    action, amount = self.raise_in_limits(math.inf, valid_actions)
            
        elif strat == 'short_shove':
            action = 'raise'
            action, amount = self.raise_in_limits(math.inf, valid_actions)
            
        
        elif strat == 'fold':
            action, amount = self.check_fold(valid_actions)
            return
        
        if action == None or amount == None:
            action = 'fold'
            amount = 0
            print('[Error] No move defined, choosing to fold')
            
        if(True):
            print(str(action)+'ing '+str(amount))
            
        return action, amount

    
def setup_ai():
    return TestBot()