#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 14:30:41 2019

@author: cyril
"""

from pypokerengine.api.game import setup_config, start_poker
from bot_TestBot import TestBot
from bot_CallBot import CallBot
from bot_PStratBot import PStratBot
from bot_HandEvaluatingBot import HandEvaluatingBot
from bot_DeepBot import DeepBot #aka Master Bot

"""
config = setup_config(max_round=20, initial_stack=3000, small_blind_amount=50)
config.register_player(name="p1", algorithm=PStratBot())
config.register_player(name="p2", algorithm=PStratBot())
config.register_player(name="p3", algorithm=PStratBot())
config.register_player(name="p4", algorithm=PStratBot())
config.register_player(name="p5", algorithm=PStratBot())
config.register_player(name="p6", algorithm=DeepBot())
game_result = start_poker(config, verbose=1)

"""
config = setup_config(max_round=10000, initial_stack=10000, small_blind_amount=50)
config.register_player(name="p1", algorithm=CallBot())
config.register_player(name="p2", algorithm=CallBot())
config.register_player(name="p3", algorithm=CallBot())
config.register_player(name="p4", algorithm=HandEvaluatingBot())
config.register_player(name="p5", algorithm=HandEvaluatingBot())
config.register_player(name="p6", algorithm=PStratBot())
game_result = start_poker(config, verbose=1)


print(game_result)
