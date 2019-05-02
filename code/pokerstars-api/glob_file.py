#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 21:46:00 2019

@author: cyril
"""

from Button import Button
from DealerButton import DealerButton
from Table import Table

import constants



def init():
    global do_moves
    do_moves = False
    global do_clicks
    do_clicks = False
    global hole_card
    hole_card = []
    global valid_actions
    valid_actions = []
    global round_state
    round_state = {}
    global round_count
    round_count = 0
    global street_price
    street_price = 0
    global previous_street
    previous_street = None

    # Creating table
    global table
    table = Table(id_='Table', image_file = constants.MENU_IMAGE_PATH+'table.png', detection_confidence=0.5)
    #Creating buttons
    global fast_fold
    fast_fold = Button(id_='Fast_fold', image_file=constants.MENU_IMAGE_PATH+'menu_fast_fold.png', detection_confidence=0.8)
    global fold
    fold = Button(id_='Fold', image_file=constants.MENU_IMAGE_PATH+'menu_fold.png', detection_confidence=0.8)
    global check
    check = Button(id_='Check', image_file=constants.MENU_IMAGE_PATH+'menu_check.png', detection_confidence=0.8)
    global call
    call = Button(id_='Call', image_file=constants.MENU_IMAGE_PATH+'menu_call.png', detection_confidence=0.65, contains_value = True)
    global raise_to
    raise_to = Button(id_='Raise_to', image_file=constants.MENU_IMAGE_PATH+'menu_raise_to.png', detection_confidence=0.7, contains_value = True)
    global bet
    bet = Button(id_='Bet', image_file=constants.MENU_IMAGE_PATH+'menu_bet.png', detection_confidence=0.65, contains_value = True)
    global bet_sizer
    bet_sizer = Button(id_='Bet_sizer', image_file=constants.MENU_IMAGE_PATH+'bet_sizer.png', detection_confidence = 0.9)
    global bet_value_box
    bet_value_box = Button(id_='Bet_value_box', image_file=constants.MENU_IMAGE_PATH+'bet_value_box.png', detection_confidence = 0.95)

    global dealer_button
    dealer_button = DealerButton(id_='Dealer_button', image_file='../../data/images/dealer_button.png', detection_confidence = 0.95)


    #Creating card relative variable
    global all_cards_found
    all_cards_found = False
    global cards
    cards = []

    #Creating player relative variables
    global all_players_found
    all_players_found = False
    global players
    players = []
    global hero_availability
    hero_availability = False

    #Creating stack relative variable
    global all_stack_containers_found
    all_stack_containers_found = False
    global stack_containers
    stack_containers = []

    #Creating bet relative variable
    global all_bet_containers_found
    all_bet_containers_found = False
    global bet_containers
    bet_containers = []
    global main_pot
    main_pot = 0
    global new_street
    new_street = True
    global previous_bet_value
    previous_bet_value = 0
    global previous_players
    previous_players = []
    global next_players
    next_players = []


    return
