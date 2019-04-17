#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 14:30:41 2019

@author: cyril
"""

from pypokerengine.api.game import setup_config, start_poker
from bot_CallBot import CallBot
from bot_PStratBot import PStratBot
from bot_HandEvaluatingBot import HandEvaluatingBot
from bot_TestBot import TestBot


"""
config = setup_config(max_round=1, initial_stack=300, small_blind_amount=5)
config.register_player(name="p1", algorithm=CallBot())
config.register_player(name="p2", algorithm=CallBot())
config.register_player(name="p3", algorithm=CallBot())
config.register_player(name="p4", algorithm=TestBot())
game_result = start_poker(config, verbose=1)

"""
config = setup_config(max_round=1000, initial_stack=10000, small_blind_amount=50)
config.register_player(name="p1", algorithm=CallBot())
config.register_player(name="p2", algorithm=CallBot())
config.register_player(name="p3", algorithm=CallBot())
config.register_player(name="p4", algorithm=HandEvaluatingBot())
game_result = start_poker(config, verbose=0)

print(game_result)