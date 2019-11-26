#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 13:15:22 2019

@author: cyril
"""
import sys
sys.path.append('../PyPokerEngine/')
sys.path.append('../poker-simul/')
import os
import random
from functools import reduce
import pickle
from bot_LSTMBot import LSTMBot
from u_formatting import get_flat_params

### GENERATE RANDOM BOTS ###
#Necessary for first generation
def gen_rand_bots(gen_dir, network='6max_full', ga_popsize=50, overwrite=True):
    #create dir for generation
    if not os.path.exists(gen_dir):
        os.makedirs(gen_dir)

    if not os.path.exists(gen_dir+'/bots'):
        os.makedirs(gen_dir+'/bots')
        ### GENERATE ALL BOTS ####
    if overwrite == True or not os.path.exists(gen_dir+'/bots/'+str(1)+'/bot_'+str(1)+'_flat.pkl'):
        full_dict = None
        for bot_id in range(1,ga_popsize+1): #there are usually 50 bots
            if not os.path.exists(gen_dir+'/bots/'+str(bot_id)):
                os.makedirs(gen_dir+'/bots/'+str(bot_id))
            lstm_bot = LSTMBot(id_= bot_id, full_dict=full_dict, network=network)
            with open(gen_dir+'/bots/'+str(lstm_bot.id)+'/bot_'+str(lstm_bot.id)+'_flat.pkl', 'wb') as f:
                pickle.dump(get_flat_params(lstm_bot.full_dict), f, protocol=0)
    return


### GENERATE ALL DECKS OF A GENERATION ####
def gen_decks(gen_dir=None, nb_hands = 300, nb_games = 1,  nb_cards = 52, overwrite = True):
    """
    gen_dir: directory of the generation ; type=string
    overwrite: whether to overwrite pre-existant decks if necessary ; type = boolean
    nb_hands: number of hands played ; type = int
    nb_cards: number of cards in the deck ; type = int
    nb_games: number of games played (by each agent) at a generation; type = int

    cst_decks: All the decks necessary for one generation; type: list of list | shape : [nb_games, nb_hands, nb_cards]
    """
    #If decks are already generated and function should not overwrite, simply load deck.
    #This happens when rerunning the same simulation.
    if gen_dir!=None and os.path.exists(gen_dir+'/cst_decks.pkl') and overwrite==False:
        with open(gen_dir+'/cst_decks.pkl', 'rb') as f:
            cst_decks = pickle.load(f)
    #Else, generate decks
    else:
        cst_decks=[0,]*nb_games
        for i in range(nb_games):
            #generating nb_games lists of nb_hands lists of size nb_cards
            cst_decks[i] = reduce(lambda x1,x2: x1+x2, [random.sample(range(1,nb_cards+1),nb_cards) for i in range(nb_hands)])
        if nb_games==1:
            cst_decks = cst_decks[0]
        if gen_dir!=None:
            with open(gen_dir+'/cst_decks.pkl', 'wb') as f:
                pickle.dump(cst_decks, f, protocol=2)

    return cst_decks
