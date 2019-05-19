#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 14:25:26 2019

@author: cyril
"""


from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
import math
from tools import value_estimator, write_declare_action_state, write_round_start_state, write_round_result_state, find_round_id, find_action_id
import itertools
from numpy.random import choice

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
            self.print_cards(round_state)
        self.street_was_raised = self.was_raised(round_state)

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
                action, amount = self.raise_in_limits(amount, valid_actions)
            else:
                amount = int(3*[action_desc['amount'] for action_desc in round_state['action_histories'][round_state['street']] if action_desc['action']=='RAISE'][-1])
                action, amount = self.raise_in_limits(amount, valid_actions)

        elif strat == 'deep_preflop_raise_fold':
            if not(self.street_was_raised):
                #call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
                amount = int((3+self.number_called(round_state))*self.big_blind_amount)
                action, amount = self.raise_in_limits(amount, valid_actions)
            else:
                action, amount = self.check_fold(valid_actions)

        elif strat == 'deep_postflop_raise_raise':
            if not(self.street_was_raised):
                #call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
                amount = int((2/3)*round_state['pot']['main']['amount'])
                action, amount = self.raise_in_limits(amount, valid_actions)
            else:
                nb_raise_before = sum([action_desc['action']=='RAISE' for action_desc in round_state['action_histories'][round_state['street']]])
                if nb_raise_before==1:
                    last_raise = [action_desc for action_desc in round_state['action_histories'][round_state['street']] if action_desc['action']=='RAISE'][-1]['amount']
                    amount = int(3*last_raise + round_state['pot']['main']['amount'])
                    action, amount = self.raise_in_limits(amount, valid_actions)
                else:
                    action, amount = self.raise_in_limits(math.inf, valid_actions)

        elif strat == 'short_shove':
            action = 'raise'
            action, amount = self.raise_in_limits(math.inf, valid_actions)


        elif strat == 'fold':
            action, amount = self.check_fold(valid_actions)

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



    def was_raised(self, round_state):
        return any([action_desc['action']=='RAISE' for action_desc in round_state['action_histories'][round_state['street']]])

    def number_called(self, round_state):
        return sum([action_desc['action']=='CALL' for action_desc in round_state['action_histories'][round_state['street']]])

    def raise_in_limits(self, amount, valid_actions):
        #if no raise available, calling
        if [item for item in valid_actions if item['action'] == 'raise'][0]['amount']['max']==-1:
            action_in_limits = 'call'
            amount_in_limits = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
        else:
            action_in_limits = 'raise'
            max_raise = [item for item in valid_actions if item['action'] == 'raise'][0]['amount']['max']
            min_raise = [item for item in valid_actions if item['action'] == 'raise'][0]['amount']['min']
            if amount>max_raise:
                if(my_verbose_upper):
                    print('Going all in')
                amount_in_limits = max_raise
            elif amount<min_raise:
                amount_in_limits = min_raise
            else:
                amount_in_limits = amount
        return action_in_limits, amount_in_limits

    def check_fold(self, valid_actions):
        # Check whether it is possible to call
        can_call = len([item for item in valid_actions if item['action'] == 'call']) > 0
        if can_call:
            # If so, compute the amount that needs to be called
            call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
        else:
            call_amount = 0
        action = 'call' if can_call and call_amount == 0 else 'fold'

        #if (my_verbose):
        #    if action =='call': print('Calling')
        #    elif action == 'fold': print('Folding')
        return action, 0

    def combi_card(self, hand_score, id_=0):
        if(id_==0):
            return int(sum([hand_score & (1<<n) for n in range(12,16)])/(2**12))
        elif(id_==1):
            return int(sum([hand_score & (1<<n) for n in range(8,12)])/(2**8))
        else:
            ##Error
            pass

    def is_strong_flush_draw(self, round_state):
        color_list = [card.suit for card in self.hole_card + gen_cards(round_state['community_card'])]
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
        """
        #todelete
        if round_state!='preflop':
            print(flush_color)
            print(self.hole_card[0].suit)
            print(self.hole_card[1].suit)
        """
        #there is a flush draw (of 4 cards)
        if ((flush_color != None)
        #hole cards are suited (and in flush draw)
        and ((self.hole_card[0].suit == self.hole_card[1].suit and self.hole_card[0].suit == flush_color)
        #hole card in flush draw is A or K
        or any([self.hole_card[j].rank in ['A','K'] for j in range(2)]))):
            if my_verbose_upper:
                print('Strong flush draw')
                self.print_cards(round_state)
            return True
        else:
            return False

    def is_strong_straight_draw(self, round_state):
        #define list of ranks of available cards
        rank_list = [card.rank for card in self.hole_card + gen_cards(round_state['community_card'])]
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
                if(my_verbose_upper):
                    print('Strong straight draw')
                    self.print_cards(round_state)
                return True
        return False

    def print_cards(self, round_state):
        print('Hole cards: ' + str(list(map(lambda x: x.__str__(), self.hole_card)))
            + ', community cards: ' +str(list(map(lambda x: x.__str__(), gen_cards(round_state['community_card'])))))


def setup_ai():
    return CallBot()
