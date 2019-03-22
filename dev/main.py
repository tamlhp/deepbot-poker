#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 14:30:41 2019

@author: cyril
"""

from pypokerengine.api.game import setup_config, start_poker
from fish_player import FishPlayerHero, FishPlayer

config = setup_config(max_round=1, initial_stack=100, small_blind_amount=5)
config.register_player(name="p1", algorithm=FishPlayerHero())
config.register_player(name="p2", algorithm=FishPlayer())
config.register_player(name="p3", algorithm=FishPlayer())
game_result = start_poker(config, verbose=0)