#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 13:15:22 2019

@author: cyril
"""

from pypokerengine.api.game import setup_config, start_poker
from bot_TestBot import TestBot
from bot_CallBot import CallBot
from bot_PStratBot import PStratBot
from bot_HandEvaluatingBot import HandEvaluatingBot
from bot_DeepBot import DeepBot #aka Master Bot


for i in range(100):
    config = setup_config(max_round=500, initial_stack=1500, small_blind_amount=15)
    config.register_player(name="p1", algorithm=PStratBot())
    config.register_player(name="p2", algorithm=PStratBot())
    config.register_player(name="p3", algorithm=PStratBot())
    config.register_player(name="p4", algorithm=PStratBot())
    config.register_player(name="p5", algorithm=PStratBot())
    config.register_player(name="p6", algorithm=DeepBot())
    game_result = start_poker(config, verbose=0)
    if(i%10==0):
        print("At game number: "+str(i))