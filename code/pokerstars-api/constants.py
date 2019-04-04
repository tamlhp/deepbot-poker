#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 21:46:00 2019

@author: cyril
"""
def init():
    #CONSTANTS
    global NB_DISPLAYS
    NB_DISPLAYS = 1

    global NB_PLAYERS
    NB_PLAYERS = 6

    global PLAYER_DET_CONFIDENCE
    PLAYER_DET_CONFIDENCE = 0.92
    global DEG_PLAYERS
    DEG_PLAYERS = [{'right':315, 'left':250},{'right':250,'left':188},{'right':188,'left':150},
                       {'right':150,'left':70},{'right':70,'left':350},{'right':350,'left':315}]

    global MENU_IMAGE_PATH
    MENU_IMAGE_PATH = "../../data/images/menu/"

    global PLAYER_IMAGE_PATH
    PLAYER_IMAGE_PATH = "../../data/images/player/"

    global PLAYER_CARDS_OFFSET
    PLAYER_CARDS_OFFSET = [40,120]

    global HOLE_CARDS_IMAGE
    HOLE_CARDS_IMAGE =  "../../data/images/hole_cards.png"
    global HOLE_CARDS_DET_CONFIDENCE
    HOLE_CARDS_DET_CONFIDENCE = 0.75

    global NUMBERS_STACK_PATH
    NUMBERS_STACK_PATH = "../../data/images/numbers/stacks/"
    global NUMBERS_STACK_DET_CONFIDENCE
    NUMBERS_STACK_DET_CONFIDENCE = 0.98

    global NUMBERS_BET_PATH
    NUMBERS_BET_PATH = "../../data/images/numbers/bets/"
    global NUMBERS_BET_DET_CONFIDENCE
    NUMBERS_BET_DET_CONFIDENCE = 0.9

    global NUMBERS_BUTTON_PATH
    NUMBERS_BUTTON_PATH = "../../data/images/numbers/buttons/"
    global NUMBERS_BUTTON_DET_CONFIDENCE
    NUMBERS_BUTTON_DET_CONFIDENCE = 0.9

    global CARD_REDET_TOL
    CARD_REDET_TOL = 20

    global RESEARCH_MARGIN
    RESEARCH_MARGIN = 1/4

    return
