#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 14:30:41 2019

@author: cyril
"""
import sys
sys.path.append('../PyPokerEngine_fork')
from pypokerengine.api.game import setup_config, start_poker
from bot_TestBot import TestBot
from bot_CallBot import CallBot
from bot_PStratBot import PStratBot
from bot_HandEvaluatingBot import HandEvaluatingBot
from bot_DeepBot import DeepBot #aka Master Bot
import time

"""
config = setup_config(max_round=1000, initial_stack=1500, small_blind_amount=15)
config.register_player(name="p1", algorithm=PStratBot())
config.register_player(name="p2", algorithm=PStratBot())
config.register_player(name="p3", algorithm=PStratBot())
config.register_player(name="p4", algorithm=PStratBot())
config.register_player(name="p5", algorithm=PStratBot())
config.register_player(name="p6", algorithm=DeepBot())
game_result = start_poker(config, verbose=1)
"""

"""
config = setup_config(max_round=10, initial_stack=10000, small_blind_amount=50)
config.register_player(name="p1", algorithm=CallBot())
config.register_player(name="p2", algorithm=HandEvaluatingBot())
config.register_player(name="p3", algorithm=HandEvaluatingBot())
config.register_player(name="p4", algorithm=PStratBot())
config.register_player(name="p5", algorithm=PStratBot())
config.register_player(name="p6", algorithm=PStratBot())
game_result = start_poker(config, verbose=0)
"""

time_1 = time.time()
config = setup_config(max_round=1000, initial_stack=200000, small_blind_amount=5)
config.register_player(name="p3", algorithm=HandEvaluatingBot())
config.register_player(name="p4", algorithm=PStratBot())
config.register_player(name="p3", algorithm=HandEvaluatingBot())
config.register_player(name="p4", algorithm=PStratBot())
config.register_player(name="p3", algorithm=HandEvaluatingBot())
config.register_player(name="p4", algorithm=PStratBot())
game_result = start_poker(config, verbose=0)
time_2 = time.time()
print(str(time_2-time_1))
print(game_result)


"""
time1 = time.time()
config = setup_config(max_round=1000, initial_stack=200000, small_blind_amount=10)
config.register_player(name="p1", algorithm=HandEvaluatingBot())
config.register_player(name="p2", algorithm=CallBot())
game_result = start_poker(config, verbose=0)

time2 = time.time()
print('Took %0.3f ms' % ((time2-time1)*1000.0))
"""
#print(game_result)
