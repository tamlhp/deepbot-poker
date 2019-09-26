#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 13:15:22 2019

@author: cyril
"""
import mkl
mkl.set_num_threads(1)
import sys
sys.path.append('../PyPokerEngine/')
sys.path.append('../poker-simul/')
from pypokerengine.api.game import setup_config, start_poker
from bot_CallBot import CallBot
from bot_ConservativeBot import ConservativeBot
from bot_ManiacBot import ManiacBot
from bot_PStratBot import PStratBot
from bot_LSTMBot import LSTMBot
from bot_CandidBot import CandidBot
from bot_EquityBot import EquityBot
import random
import pickle
import numpy as np
import time
from multiprocessing import Pool
import os
from functools import reduce
from collections import OrderedDict
from neuroevolution import get_flat_params

### GENERATE RANDOM BOTS ###
#Necessary for first generation
def gen_rand_bots(simul_id, gen_id, log_dir = './simul_data', overwrite=True, nb_bots=50, network='first'):
    #create dir for generation
    gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    if not os.path.exists(gen_dir):
        os.makedirs(gen_dir)

    if not os.path.exists(gen_dir+'/bots'):
        os.makedirs(gen_dir+'/bots')
        ### GENERATE ALL BOTS ####
    if overwrite == True or not os.path.exists(gen_dir+'/bots/'+str(1)+'/bot_'+str(1)+'_flat.pkl'):
        full_dict = None
        for bot_id in range(1,nb_bots+1): #there are usually 50 bots
            if not os.path.exists(gen_dir+'/bots/'+str(bot_id)):
                os.makedirs(gen_dir+'/bots/'+str(bot_id))
            lstm_bot = LSTMBot(id_= bot_id, full_dict=full_dict, gen_dir = gen_dir, network=network)
            with open(gen_dir+'/bots/'+str(lstm_bot.id)+'/bot_'+str(lstm_bot.id)+'_flat.pkl', 'wb') as f:
                pickle.dump(get_flat_params(lstm_bot.full_dict), f, protocol=0)
    return

### GENERATE ALL DECKS OF A GENERATION ####
def gen_decks(gen_dir, overwrite = True, nb_hands = 300,  nb_cards = 52, nb_games = 1):
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
    if os.path.exists(gen_dir+'/cst_decks.pkl') and overwrite==False:
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
        with open(gen_dir+'/cst_decks.pkl', 'wb') as f:
            pickle.dump(cst_decks, f, protocol=2)

    return cst_decks
