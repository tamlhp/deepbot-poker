#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 04:25:39 2019

@author: cyril
"""


from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card, gen_cards
import math
from utils_bot import raise_in_limits, fold_in_limits, is_strong_flush_draw, is_strong_straight_draw, was_raised, print_cards

#import itertools

my_verbose = False
my_verbose_upper = False

class PStratBot(BasePokerPlayer):

    SUIT_MAP = {2  : 'C',  4  : 'D',   8  : 'H',   16 : 'S'}
    RANK_INV_MAP = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}

    def __init__(self):
        super().__init__()
        self.hole_card = ['','']
        self.hole_card_num = ['','']
        self.pos_group = ''
        self.street_was_raised = None
        self.num_players = 6

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        #print(str(round_state) + '\n')
        #hole_card = ['DK', 'HJ']
        #round_state['community_card'] = ['HK', 'S8', 'DQ']

        """
        print("hole_card:" + str(hole_card))
        print("valid_actions:"+ str(valid_actions))
        print("round_state:"+str(round_state))
        """
        """
        #DEBUGGING
        valid_actions = [{'action': 'fold', 'amount': 0}, {'action': 'call', 'amount': 100}, {'action': 'raise', 'amount': {'min': 150, 'max': 10000}}]
        hole_card = ['S2','S4']
        round_state = {'action_histories':
        {'turn': [{'paid': 0, 'uuid': 'dsitwxjfzukumvtbxangpv', 'action': 'CALL', 'amount': 0},
                  {'paid': 0, 'uuid': 'kydxboxhgkqcosfunbpkxs', 'action': 'CALL', 'amount': 0}],
        'preflop': [{'add_amount': 50, 'uuid': 'dsitwxjfzukumvtbxangpv', 'action': 'SMALLBLIND', 'amount': 50},
                    {'add_amount': 50, 'uuid': 'kydxboxhgkqcosfunbpkxs', 'action': 'BIGBLIND', 'amount': 100},
                    {'action': 'FOLD', 'uuid': 'xkrwhpjormlqgduzvsivsb'},
                    {'paid': 100, 'uuid': 'wywinfwqxcrtocydvsszbc', 'action': 'CALL', 'amount': 100},
                    {'paid': 50, 'uuid': 'dsitwxjfzukumvtbxangpv', 'action': 'CALL', 'amount': 100},
                    {'paid': 0, 'uuid': 'kydxboxhgkqcosfunbpkxs', 'action': 'CALL', 'amount': 100}],
        'flop': [{'paid': 0, 'uuid': 'dsitwxjfzukumvtbxangpv', 'action': 'CALL', 'amount': 0},
                 {'paid': 0, 'uuid': 'kydxboxhgkqcosfunbpkxs', 'action': 'CALL', 'amount': 0},
                 {'paid': 0, 'uuid': 'wywinfwqxcrtocydvsszbc', 'action': 'CALL', 'amount': 0}]},
        'community_card': ['HQ', 'S2', 'HQ', 'D5'], 'pot': {'main': {'amount': 300}, 'side': []},
        'street': 'turn', 'dealer_btn': 0, 'next_player': 0, 'small_blind_amount': 50,
        'seats': [{'state': 'participating', 'name': 'p1', 'uuid': 'wywinfwqxcrtocydvsszbc', 'stack': 9900},
                  {'state': 'participating', 'name': 'p2', 'uuid': 'dsitwxjfzukumvtbxangpv', 'stack': 9900},
                  {'state': 'participating', 'name': 'p3', 'uuid': 'kydxboxhgkqcosfunbpkxs', 'stack': 9900},
                  {'state': 'folded', 'name': 'p4', 'uuid': 'xkrwhpjormlqgduzvsivsb', 'stack': 10000}],
        'small_blind_pos': 1, 'big_blind_pos': 2, 'round_count': 1}

        """

        self.hole_card = gen_cards(hole_card)
        if self.hole_card[0].rank<self.hole_card[1].rank:
            self.hole_card = [self.hole_card[1],self.hole_card[0]]

        self.pos_group = self.define_position(round_state = round_state, player_id = round_state['next_player'])
        self.big_blind_amount = round_state['small_blind_amount']*2

        self.street_was_raised = was_raised(round_state)

        if my_verbose_upper:
            print_cards(hole_card, round_state)
            print('Position group: ' +str(self.pos_group))
            print('Main pot: '+ str(round_state['pot']['main']['amount']))
            if self.street_was_raised:
                print('Street was raised')

        strat = self.define_strat(round_state)
        if my_verbose_upper:
            print('Chosen strat: '+ str(strat))
        action, amount = self.define_action(strat, round_state, valid_actions)
                
        if round_state['street'] == 'preflop':
            print(self.pos_group)
            #print([card.rank for card in self.hole_card])
            #print(round_state['community_card'])
            print(action)
        return action, amount   # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        self.num_players = game_info['player_num']
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        #self.hole_card = gen_cards(hole_card)
        #self.pos_group = ''
        pass

    def receive_street_start_message(self, street, round_state):
        #if(street=='preflop'):
        #    self.pos_group = self.define_position(round_state)
        return

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass


    def define_strat(self, round_state):
        hero_BBs = round_state['seats'][round_state['next_player']]['stack']/self.big_blind_amount
        #if Hero has more than 12 BB
        if (hero_BBs>12):
            if(round_state['street']=='preflop'): #preflop
                ### Go through possible cases ###
                #holding AA, KK, QQ or AK
                if(self.hand_in_range(['A'],['Q'], pocket = True)
                or self.hand_in_range(['A'],['K'])):
                    strat = 'deep_preflop_raise_raise'
                #holding JJ
                elif(self.hand_in_range(['J'],['J'], pocket = True)):
                    if self.pos_group in ['early','middle']: strat = 'deep_preflop_raise_fold'
                    elif self.pos_group in ['blinds','late']: strat = 'deep_preflop_raise_raise'
                #holding TT, 99, 88 or AQ
                elif(self.hand_in_range(['T'],['8'], pocket = True)
                or self.hand_in_range(['A'],['Q'])):
                    if self.pos_group in ['early']: strat = 'fold'
                    elif self.pos_group in ['middle','blinds','late']: strat = 'deep_preflop_raise_fold'
                #holding 77, AJ, AT, KQ or KJ
                elif(self.hand_in_range(['7'],['7'], pocket = True)
                or self.hand_in_range(['A','K'],['T','J'])):
                    if self.pos_group in ['early','middle']: strat = 'fold'
                    elif self.pos_group in ['late','blinds']: strat = 'deep_preflop_raise_fold'
                else:
                    strat = 'fold'

            else: #postflop
                ### Go through possible cases ###
                hand_score = HandEvaluator.eval_hand(self.hole_card,gen_cards(round_state['community_card']))
                if (my_verbose):
                    print('Hand: ' + "{0:b}".format(hand_score))
                three_of_a_kind_score = (1<<18)
                two_pair_score = (1<<17)
                pair_score = (1<<16)

                #hand is two-pair or better
                if(hand_score >= three_of_a_kind_score):
                    strat = 'deep_postflop_raise_raise'
                elif(hand_score & two_pair_score
                #hole cards used in double pair
                and all([card.rank in [self.combi_card(hand_score, i) for i in range(2)] for card in self.hole_card])
                #player holds card involved in top pair (or better)
                and self.hole_card[0].rank >= self.combi_card(hand_score)):
                    strat = 'deep_postflop_raise_raise'
                #player has a pair
                elif(hand_score &  pair_score
                #a hole card is used in pair
                and any([card.rank == self.combi_card(hand_score, i) for card in self.hole_card for i in range(2)])
                #pair is top
                and all([self.combi_card(hand_score)>=card.rank for card in gen_cards(round_state['community_card'])])):
                    strat = 'deep_postflop_raise_raise'
                #strong draws on flop or turn
                elif(round_state['street'] in ['flop','turn']
                and (is_strong_flush_draw(hole_card = self.hole_card, round_state=round_state, my_verbose=my_verbose) or is_strong_straight_draw(hole_card = self.hole_card, round_state = round_state, my_verbose=my_verbose))):
                    strat = 'deep_postflop_raise_raise'
                else:
                    strat = 'fold'

        #if Hero has 12 BB or less
        else:
            strat = 'fold'
            if not(self.street_was_raised):
                #early and middle
                if self.pos_group in ['early','middle']:
                    #between 9 and 12 BBs
                    if (hero_BBs<=12 and hero_BBs>9):
                        #offsuit cards
                        if ((self.hand_in_range(['A'],['Q']))
                        #suited cards
                        or (self.hand_in_range(['A'],['T'], suited = True))
                        #pockets
                        or (self.hand_in_range(['A'],['6'], pocket = True))):
                            strat = 'short_shove'
                    #between 6 and 9 BBs
                    elif(hero_BBs<=9 and hero_BBs>5):
                        #offsuit cards
                        if ((self.hand_in_range(['A','K','Q','J'],['T','T','T','T']))
                        #suited cards
                        or (self.hand_in_range(['A','K','Q','J','T','9'],['2','4','8','7','7','8'], suited = True))
                        #pockets
                        or (self.hand_in_range(['A'],['2'], pocket = True))):
                            strat = 'short_shove'
                    elif(hero_BBs<5):
                        #offsuit cards
                        if ((self.hand_in_range(['A','K','Q','J'],['2','8','T','T']))
                        #suited cards
                        or (self.hand_in_range(['A','K','Q','J','T','9','8','7','6'],['2','4','6','7','6','6','6','5','5'], suited = True))
                        #pockets
                        or (self.hand_in_range(['A'],['2'], pocket = True))):
                            strat = 'short_shove'
                elif(self.pos_group in ['late','blinds']):
                        #offsuit cards
                        if ((self.hand_in_range(['A','K','Q','J','T'],['2','4','9','9','9']))
                        #suited cards
                        or (self.hand_in_range(['A','K','Q','J','T','9','8','7','6'],['2','2','2','7','6','6','6','5','5'], suited = True))
                        #pockets
                        or (self.hand_in_range(['A'],['2'], pocket = True))):
                            strat = 'short_shove'

            #opponent raised before hero
            elif(self.street_was_raised):
                raiser_uuid = [action_desc['uuid'] for action_desc in round_state['action_histories'][round_state['street']] if action_desc['action']=='RAISE'][-1]
                raiser_id = [player['uuid']==raiser_uuid for player in round_state['seats']].index(True)
                raiser_pos_group = self.define_position(round_state = round_state, player_id = raiser_id)
                raiser_BBs = round_state['seats'][raiser_id]['stack']/self.big_blind_amount
                if raiser_pos_group == 'early':
                    #offsuit cards
                    if (self.hand_in_range(['A'],['Q'])):
                        strat =  'short_shove'
                    elif (raiser_BBs<=12 and raiser_BBs>6):
                        #pockets
                        if (self.hand_in_range(['A'],['T'], pocket = True)):
                            strat = 'short_shove'
                    else:
                        #pockets
                        if (self.hand_in_range(['A'],['8'], pocket = True)):
                            strat = 'short_shove'
                elif raiser_pos_group == 'middle':
                    #pocket cards
                    if (self.hand_in_range(['A'],['7'], pocket = True)):
                            strat = 'short_shove'
                    elif (raiser_BBs<=12 and raiser_BBs>6):
                        #offsuit cards
                        if (self.hand_in_range(['A'],['Q'])):
                            strat =  'short_shove'
                    else:
                        #offsuit cards
                        if (self.hand_in_range(['A'],['J'])):
                            strat =  'short_shove'

                elif raiser_pos_group == 'late':
                    #pocket cards
                    if (self.hand_in_range(['A'],['5'], pocket = True)):
                            strat = 'short_shove'
                    elif (raiser_BBs<=12 and raiser_BBs>6):
                        #offsuit cards
                        if (self.hand_in_range(['A','K'],['T','Q'])):
                            strat =  'short_shove'
                        #suited cards
                        elif (self.hand_in_range(['A','K'],['7','Q'], suited = True)):
                            strat =  'short_shove'
                    else:
                        #offsuit cards
                        if (self.hand_in_range(['A','K','Q'],['5','T','J'])):
                            strat =  'short_shove'
                elif raiser_pos_group == 'blinds':
                    #pocket cards
                    if (self.hand_in_range(['A'],['2'], pocket = True)):
                            strat = 'short_shove'
                    elif (raiser_BBs<=12 and raiser_BBs>6):
                        #offsuit cards
                        if (self.hand_in_range(['A','K'],['8','Q'])):
                            strat =  'short_shove'
                        #suited cards
                        elif (self.hand_in_range(['A','K'],['2','Q'], suited = True)):
                            strat =  'short_shove'
                    else:
                        #offsuit cards
                        if (self.hand_in_range(['A','K','Q','J'],['2','T','J','T'])):
                            strat =  'short_shove'

        #print(card for card in self.hole_card)
        if my_verbose_upper:
            print('Following strat: ' + strat)
        return strat

    def define_action(self, strat, round_state, valid_actions):
        action = None
        amount = None

        if strat == 'deep_preflop_raise_raise':
            if not(self.street_was_raised):
                #call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
                amount = int((3+self.number_called(round_state))*self.big_blind_amount)
                action, amount = raise_in_limits(amount, valid_actions, my_verbose_upper)
            else:
                amount = int(3*[action_desc['amount'] for action_desc in round_state['action_histories'][round_state['street']] if action_desc['action']=='RAISE'][-1])
                action, amount = raise_in_limits(amount, valid_actions, my_verbose_upper)

        elif strat == 'deep_preflop_raise_fold':
            if not(self.street_was_raised):
                #call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
                amount = int((3+self.number_called(round_state))*self.big_blind_amount)
                action, amount = raise_in_limits(amount, valid_actions, my_verbose_upper)
            else:
                action, amount = fold_in_limits(valid_actions, my_verbose)

        elif strat == 'deep_postflop_raise_raise':
            if not(self.street_was_raised):
                #call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
                amount = int((2/3)*round_state['pot']['main']['amount'])
                action, amount = raise_in_limits(amount, valid_actions, my_verbose_upper)
            else:
                nb_raise_before = sum([action_desc['action']=='RAISE' for action_desc in round_state['action_histories'][round_state['street']]])
                if nb_raise_before==1:
                    last_raise = [action_desc for action_desc in round_state['action_histories'][round_state['street']] if action_desc['action']=='RAISE'][-1]['amount']
                    amount = int(3*last_raise + round_state['pot']['main']['amount'])
                    action, amount = raise_in_limits(amount, valid_actions, my_verbose_upper)
                else:
                    action, amount = raise_in_limits(math.inf, valid_actions, my_verbose_upper)

        elif strat == 'short_shove':
            action = 'raise'
            action, amount = raise_in_limits(math.inf, valid_actions, my_verbose_upper)


        elif strat == 'fold':
            action, amount = fold_in_limits(valid_actions, my_verbose)

        if action == None or amount == None:
            action = 'fold'
            amount = 0
            print('[Error] No move defined, choosing to fold')

        if my_verbose_upper:
            print(str(action)+'ing '+str(amount))

        return action, amount


    def define_position(self, round_state, player_id):
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
    return PStratBot()
