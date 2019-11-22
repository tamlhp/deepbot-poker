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

    global CARD_DET_CONFIDENCE
    CARD_DET_CONFIDENCE = 0.9
    global CARD_PATH
    CARD_PATH = '../../data/api-images/cards/card_'

    global PLAYER_DET_CONFIDENCE
    PLAYER_DET_CONFIDENCE = 0.92
    global DEG_PLAYERS
    DEG_PLAYERS = [{'right':315, 'left':250},{'right':250,'left':188},{'right':188,'left':150},
                       {'right':150,'left':70},{'right':70,'left':350},{'right':350,'left':315}]

    global MENU_IMAGE_PATH
    MENU_IMAGE_PATH = "../../data/api-images/menu/"

    global PLAYER_IMAGE_PATH
    PLAYER_IMAGE_PATH = "../../data/api-images/player/"

    global PLAYER_CARDS_OFFSET
    PLAYER_CARDS_OFFSET = [40,120]

    global HOLE_CARDS_IMAGE
    HOLE_CARDS_IMAGE =  "../../data/api-images/hole_cards.png"
    global HOLE_CARDS_DET_CONFIDENCE
    HOLE_CARDS_DET_CONFIDENCE = 0.75

    global NUMBERS_STACK_PATH
    NUMBERS_STACK_PATH = "../../data/api-images/numbers/stacks/"
    global NUMBERS_STACK_DET_CONFIDENCE
    NUMBERS_STACK_DET_CONFIDENCE = 0.98

    global NUMBERS_BET_PATH
    NUMBERS_BET_PATH = "../../data/api-images/numbers/bets/"
    global NUMBERS_BET_DET_CONFIDENCE
    NUMBERS_BET_DET_CONFIDENCE = 0.9

    global NUMBERS_BUTTON_PATH
    NUMBERS_BUTTON_PATH = "../../data/api-images/numbers/buttons/"
    global NUMBERS_BUTTON_DET_CONFIDENCE
    NUMBERS_BUTTON_DET_CONFIDENCE = 0.9

    global CARD_REDET_TOL
    CARD_REDET_TOL = 20

    global RESEARCH_MARGIN
    RESEARCH_MARGIN = 1/4

    global HERO_POSITION
    HERO_POSITION = 0

    global MAX_SBS_FOR_CLICKRAISE
    MAX_SBS_FOR_CLICKRAISE = 6

    global POT_ZONE_LENGTH
    POT_ZONE_LENGTH = 50

    global INV_RANK_MAP
    INV_RANK_MAP = {
          '2' : 2,
          '3' : 3,
          '4' : 4,
          '5' : 5,
          '6' : 6,
          '7' : 7,
          '8' : 8,
          '9' : 9,
          'T' : 10,
          'J' : 11,
          'Q' : 12,
          'K' : 13,
          'A' : 14
      }

    return
