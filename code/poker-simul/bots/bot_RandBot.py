#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 14:25:26 2019

@author: cyril
"""


from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards
import math
#from u_utils import value_estimator, write_declare_action_state, write_round_start_state, write_round_result_state, find_round_id, find_action_id
from random import randint
from numpy.random import choice
from utils_bot import raise_in_limits, fold_in_limits, print_cards, was_raised
from utils_io import write_declare_action_state, write_round_start_state, write_round_result_state, find_action_id, find_round_id


my_verbose = False
my_verbose_upper = False
HAND_DATA_DECLARE_ACTION_CSV = '../../data/hand-data/test_action_declare.csv'
HAND_DATA_ROUND_RESULT_CSV = '../../data/hand-data/test_round_result.csv'
HAND_DATA_ROUND_START_CSV = '../../data/hand-data/test_round_start.csv'

class DeepBot(BasePokerPlayer): #aka Master Bot  # Do not forget to make parent class as "BasePokerPlayer"

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        self.hole_card = gen_cards(hole_card)
        self.pos_group = self.define_position(round_state)

        if my_verbose_upper:
            print_cards(hole_card, round_state)
        self.street_was_raised = was_raised(round_state)

        strat = self.define_strat(round_state)
        action, amount = self.define_action(strat, round_state, valid_actions)
        #print(round_state)
        write_declare_action_state(action_id = self.action_id, round_id = self.round_id, valid_actions = valid_actions,
                                   hole_card = hole_card, round_state = round_state, strat=strat, action=action, amount = amount,
                                   csv_file = HAND_DATA_DECLARE_ACTION_CSV)
        self.action_id+=1
        return action, amount   # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        self.num_players = game_info['player_num']
        self.big_blind_amount = game_info['rule']['small_blind_amount']*2
        self.action_id = find_action_id(csv_file = HAND_DATA_DECLARE_ACTION_CSV)
        self.round_id = find_round_id(csv_file = HAND_DATA_ROUND_RESULT_CSV)
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        #print(seats)
        write_round_start_state(round_id = self.round_id, seats = seats, csv_file = HAND_DATA_ROUND_START_CSV)
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        write_round_result_state(round_id = self.round_id, winners = winners,
                                 hand_info = hand_info, round_state = round_state, csv_file = HAND_DATA_ROUND_RESULT_CSV)
        self.round_id+=1
        pass


    def define_strat(self, round_state):
        strategies = ['deep_preflop_raise_fold', 'deep_preflop_raise_raise', 'deep_postflop_raise_raise', 'short_shove', 'fold']
        strat_weights = [0.15,0.15,0.15,0.15,0.4]

        #values = [value_estimator(round_state, strat) for strat in strategies]
        #best_strat = strategies[values.index([vals for vals in sorted(values, reverse = True)][0])]

        best_strat = choice(strategies, p=strat_weights)


        return best_strat

    def define_action(self, strat, round_state, valid_actions):
        action = None
        amount = None

        if strat == 'deep_preflop_raise_raise':
            if not(self.street_was_raised):
                #call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
                amount = int((3+self.number_called(round_state))*self.big_blind_amount)
                action, amount = raise_in_limits(amount, valid_actions, my_verbose)
            else:
                amount = int(3*[action_desc['amount'] for action_desc in round_state['action_histories'][round_state['street']] if action_desc['action']=='RAISE'][-1])
                action, amount = raise_in_limits(amount, valid_actions, my_verbose)

        elif strat == 'deep_preflop_raise_fold':
            if not(self.street_was_raised):
                #call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
                amount = int((3+self.number_called(round_state))*self.big_blind_amount)
                action, amount = raise_in_limits(amount, valid_actions, my_verbose)
            else:
                action, amount = fold_in_limits(valid_actions, my_verbose)

        elif strat == 'deep_postflop_raise_raise':
            if not(self.street_was_raised):
                #call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
                amount = int((2/3)*round_state['pot']['main']['amount'])
                action, amount = raise_in_limits(amount, valid_actions, my_verbose)
            else:
                nb_raise_before = sum([action_desc['action']=='RAISE' for action_desc in round_state['action_histories'][round_state['street']]])
                if nb_raise_before==1:
                    last_raise = [action_desc for action_desc in round_state['action_histories'][round_state['street']] if action_desc['action']=='RAISE'][-1]['amount']
                    amount = int(3*last_raise + round_state['pot']['main']['amount'])
                    action, amount = raise_in_limits(amount, valid_actions, my_verbose)
                else:
                    action, amount = raise_in_limits(math.inf, valid_actions, my_verbose)

        elif strat == 'short_shove':
            action = 'raise'
            action, amount = raise_in_limits(math.inf, valid_actions, my_verbose)


        elif strat == 'fold':
            action, amount = fold_in_limits(valid_actions, my_verbose)

        if action == None or amount == None:
            action = 'fold'
            amount = 0
            print('[Error] No move defined, choosing to fold')

        if my_verbose_upper:
            print(str(action)+'ing '+str(amount))

        return action, amount

    def define_position(self, round_state, player_id = 'Hero'):
        if player_id=='Hero':
            rel_pos = (round_state['next_player']-round_state['small_blind_pos'])%self.num_players
        else:
            rel_pos = (player_id-round_state['small_blind_pos'])%self.num_players
        if (rel_pos<=1):
            pos_group = 'blinds'
        elif (rel_pos>=self.num_players-2):
            pos_group = 'late'
        elif (rel_pos>=self.num_players-5):
            pos_group = 'middle'
        else:
            pos_group = 'early'
        return pos_group

    def hand_in_range(self, hands_max, hands_min, suited = False, pocket=False):


        #regular hand
        if not(pocket):
            if len(hands_max)!=len(hands_min):
                print('[Error] There must be the same amount of hand extremums')
                return False
            elif suited and self.hole_card[0].suit!=self.hole_card[1].suit:
                return False
            for i in range(len(hands_max)):
                if (self.hole_card[0].rank==self.RANK_INV_MAP[hands_max[i]]
                and self.hole_card[1].rank in range(self.RANK_INV_MAP[hands_min[i]], self.RANK_INV_MAP[hands_max[i]])):
                    return True

        #pockets
        elif pocket:
            if(len(hands_max)>1 or len(hands_min)>1):
                print('[Error] Expecting only one hand range to estimate pocket hand')
                return False
            if(self.hole_card[0].rank==self.hole_card[1].rank
            and self.hole_card[0].rank<=self.RANK_INV_MAP[hands_max[0]]
            and self.hole_card[0].rank>=self.RANK_INV_MAP[hands_min[0]]):
                return True


        return False



    def number_called(self, round_state):
        return sum([action_desc['action']=='CALL' for action_desc in round_state['action_histories'][round_state['street']]])


    def combi_card(self, hand_score, id_=0):
        if(id_==0):
            return int(sum([hand_score & (1<<n) for n in range(12,16)])/(2**12))
        elif(id_==1):
            return int(sum([hand_score & (1<<n) for n in range(8,12)])/(2**8))
        else:
            ##Error
            pass


def setup_ai():
    return DeepBot()





def value_estimator(round_state, strat):

    value = randint(1,10)
    return value
