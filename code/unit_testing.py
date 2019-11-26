#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 16:16:37 2019

@author: cyril
"""

import sys
sys.path.append('./PyPokerEngine')
sys.path.append('./bots')
sys.path.append('./main_functions')
from pypokerengine.api.game import setup_config, start_poker
from bot_TestBot import TestBot
from bot_CallBot import CallBot
from bot_PStratBot import PStratBot
from bot_LSTMBot import LSTMBot
from bot_EquityBot import EquityBot
from bot_ManiacBot import ManiacBot
from bot_CandidBot import CandidBot
from bot_ConservativeBot import ConservativeBot
import time
import pickle
from functools import reduce
from u_generate import gen_decks, gen_rand_bots
from u_neuroevolution import mutate_bots, crossover_bots
from u_formatting import get_full_dict, get_flat_params
import random
import os
import argparse
import numpy as np

## Parse arguments###
parser = argparse.ArgumentParser(description='')
parser.add_argument('--neural_network',  default='6max_full', type=str, help='Neural network architecture to use. [hu_first, hu_second, 6max_single, 6max_full]')
args = parser.parse_args()
my_network = args.neural_network

#constants#
gen_dir='../../data/simul_data/simul_test_functions/gen_0'

####################
print("\n## Verifying gen_rand_bots(..) ##")
func_correct = True
ga_popsize = 10
len_params_6_max_full = 24971
gen_rand_bots(gen_dir = gen_dir, network=my_network, ga_popsize = ga_popsize, overwrite=True)
#verifying amount of bots created
if len([name for name in os.listdir(gen_dir+'/bots/')]) != ga_popsize:
    print('[WARNING] Failed to create correct amount of bots. Should be '+str(ga_popsize)+' but is '+str(len([name for name in os.listdir(gen_dir+'/bots/')]))+'.')
    func_correct = False
else:
    print('Created correct amount of bots ('+str(ga_popsize)+').')
#verifying amount of parameters created for each bot
size_correct = True
for bot_id in os.listdir(gen_dir+'/bots/'):
    with open(gen_dir+'/bots/'+str(bot_id)+'/'+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:
        lstm_bot_flat = pickle.load(f)
        if(my_network =='6max_full'):
            if len(lstm_bot_flat)!=len_params_6_max_full:
                print(len(lstm_bot_flat))
                size_correct = False
                func_correct = False
        else:
            print('[WARNING] Must set up test for network '+str(my_network))
if not size_correct:
    print('[WARNING] One or multiple generated bots does not have the correct amount of parameters')
else:
    print('The generated bots have the correct amount of parameters.')
if func_correct:
    print('=>Function gen_rand_bots(..) is working correctly.')
else:
    print('=>[WARNING] Function gen_rand_bots(..) is not working as expected.')

####################
print("\n## Verifying gen_decks(..) ##")
func_correct = True
nb_hands = 100
my_nb_games = 4
nb_cards = 52
gen_decks(gen_dir = gen_dir, nb_hands=nb_hands, nb_games=my_nb_games, nb_cards = nb_cards, overwrite=False)
#Load decks
with open(gen_dir+'/cst_decks.pkl', 'rb') as f:
    cst_decks = pickle.load(f)
#verifying number of games generated
if len(cst_decks)!=my_nb_games:
    func_correct=False
    print("[WARNING] Failed to generate the correct amount of games. Should be "+str(my_nb_games)+" but is "+str(len(cst_decks))+".")
else:
    print("Generated correct amount of games ("+str(my_nb_games)+").")
if len(cst_decks[0])!=nb_hands*nb_cards:
    func_correct=False
    print("[WARNING] Failed to generate the correct amount of cards per game. Shoud be "+str(nb_hands*nb_cards)+" but is " +str(len(cst_decks[0]))+".")
else:
    print("Generated the correct amount of cards per game ("+str(nb_hands*nb_cards)+").")
if func_correct:
    print('=>Function gen_decks(..) is working correctly.')
else:
    print('=>[WARNING] Function gen_decks(..) is not working as expected.')

####################
print("\n## Verifying get_flat_params(..) and get_full_dict(..) ##")
#The test here is performed by verifying that get_flat_params(..)
# and get_full_dict(..) are inverse functions of one another
func_correct = True
ref_full_dict = LSTMBot(network=my_network).full_dict
##verifying get_flat_params and get_full_dict
lstm_cre = LSTMBot(network=my_network)
lstm_cre_flat_params = get_flat_params(lstm_cre.full_dict)
lstm_cre_full_dict = get_full_dict(all_params = lstm_cre_flat_params, ref_full_dict = ref_full_dict)
#if(lstm_cre_full_dict == lstm_cre.full_dict):
if not(lstm_cre_full_dict.keys()==lstm_cre.full_dict.keys()):
    print("[WARNING] Dictionnary keys are not consistent")
    func_correct = False
else:
    print("Dictionnary keys are consistent")
#print(lstm_cre_full_dict.values()==lstm_cre.full_dict.values())
val_correct = True
for key in lstm_cre.full_dict.keys():
    if lstm_cre.full_dict[key].tolist()!=lstm_cre_full_dict[key].tolist():
        val_correct = False
        func_correct = False
if not val_correct:
    print("[WARNING] Dictionnary values are not consistent")
else:
    print("Dictionnary values are consistent")
if func_correct:
    print('=>Functions get_flat_params(..) and get_full_dict(..) are working correctly.')
else:
    print('=>[WARNING] Function get_flat_params(..) and get_full_dict(..) are not working as expected.')

####################
print("\n## Verifying mutate_bots(..) ##")
func_correct = True
ref_full_dict = LSTMBot(network=my_network).full_dict
lstm_first = LSTMBot(id_=1, network=my_network)
first_flat = get_flat_params(lstm_first.full_dict)
mut_rate = 0.15
mut_strength = 0.25
mutant_flat = mutate_bots(orig_bots_flat=[first_flat], nb_new_bots=1,
                                          mut_rate=mut_rate, mut_strength=mut_strength)[0]
#verifying that the right amount of values have added noise (the mutation rate)
mut_rate_tol_factor = 1.1
eff_mut_rate = sum(np.array(first_flat)!=np.array(mutant_flat))/len(first_flat)
if eff_mut_rate < mut_rate/mut_rate_tol_factor:
    print("[WARNING] Effective mutation rate is too low. Should be "+str(mut_rate)+" but is "+str(eff_mute_rate)+".")
elif eff_mut_rate > mut_rate*mut_rate_tol_factor:
    print("[WARNING] Effective mutation rate is too high. Should be "+str(mut_rate)+" but is "+str(eff_mute_rate)+".")
else:
    print("Mutation rate is respected with a tolerance of "+str(int((mut_rate_tol_factor-1)*100))+"%.")
#verifying that reasonnable amount of noise is added (the mutation strength)
mut_strength_tol_factor = 1.1
eff_mut_strength = np.average(np.abs(np.array(first_flat)-np.array(mutant_flat)))/(0.15*np.sqrt(2/np.pi))
if eff_mut_strength < mut_strength/mut_strength_tol_factor:
    print("[WARNING] Effective mutation strength is too low. Should be "+str(mut_strength)+" but is "+str(eff_mute_rate)+".")
elif eff_mut_strength > mut_strength*mut_strength_tol_factor:
    print("[WARNING] Effective mutation strength is too high. Should be "+str(mut_strength)+" but is "+str(eff_mute_rate)+".")
else:
    print("Mutation strength is respected with a tolerance of "+str(int((mut_strength_tol_factor-1)*100))+"%.")

if func_correct:
    print('=>Function mutate_bots(..) is working correctly.')
else:
    print('=>[WARNING] Function mutate_bots(..) is not working as expected.')

####################
print("\n## Verifying crossover_bots(..) ##")
func_correct = True
ref_full_dict = LSTMBot(network=my_network).full_dict
lstm_first = LSTMBot(id_=1, network=my_network)
lstm_second = LSTMBot(id_=2, network=my_network)
cross_flat = crossover_bots([get_flat_params(lstm_first.full_dict),get_flat_params(lstm_second.full_dict)], ref_full_dict = ref_full_dict, nb_new_bots = 1)[0]
cross_dict = get_full_dict(all_params = cross_flat, ref_full_dict = ref_full_dict)
lstm_cross = LSTMBot(id_=4, full_dict = cross_dict, network=my_network)
#verifying that key of layers are the same
if(lstm_cross.full_dict.keys() != lstm_first.full_dict.keys() or lstm_cross.full_dict.keys() != lstm_second.full_dict.keys()):
    print("[WARNING] Layer structure of child is not consistent with parents.")
else:
    print("Layer structure of child is consistent with parents.")

#verifying that parameters come from either of parents
parent_correct=True
for key in ref_full_dict:
    if key != 'lin_dec_1.weight':
        if lstm_cross.full_dict[key].tolist()!=lstm_first.full_dict[key].tolist() and lstm_cross.full_dict[key].tolist()!=lstm_second.full_dict[key].tolist():
            parent_correct=False
            func_correct = False
if parent_correct:
    print("Each layer of parameters in child is succesfully coming from one of the two parents.")
else:
    print("[WARNING] One or multiple layers of parameters of child are coming from neither parents.")
if func_correct:
    print('=>Function crossover_bots(..) is working correctly.')
else:
    print('=>[WARNING] Function crossover_bots(..) is not working as expected.')
