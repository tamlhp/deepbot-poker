#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 13:02:30 2019

@author: cyril
"""
import pickle
import numpy as np
import matplotlib.pyplot as plt

nb_cards = 52
nb_hands = 500

###CONSTANTS
ga_popsize= 1
simul_id = 'simul_-2_mut'
log_dir = '../../../backed_simuls/'
sb_amount = 50
ini_stack = 20000
nb_generations = 250
bot_id = 1
my_network='second'
my_dpi=100
nb_measures=10

outputs_deepbot = []
outputs_mutant = [[],[],[],[],[],[],[],[],[],[]]
mut_ids=np.arange(1,nb_measures)
for gen_id in range(50):
    gen_dir=log_dir+str(simul_id)+'/gen_'+str(gen_id)
    with open(gen_dir+'/outputs_0.pkl', 'rb') as fr:
        try:
            while True:
                outputs_deepbot.append(pickle.load(fr))
        except EOFError:
            pass
    for i,mut_id in enumerate(mut_ids):
        with open(gen_dir+'/outputs_'+str(mut_id)+'.pkl', 'rb') as fr:
            try:
                while True:
                    outputs_mutant[i].append(pickle.load(fr))
            except EOFError:
                pass

outputs_deepbot=np.array(outputs_deepbot)
outputs_dif_avg=[0,]*nb_measures
outputs_dif_std=[0,]*nb_measures
for i,mut_id in enumerate(mut_ids):     
    outputs_mutant[i]=np.array(outputs_mutant[i])
    outputs_dif = np.absolute(outputs_deepbot-outputs_mutant[i])
    outputs_dif_avg[i] = np.average(outputs_dif)
    outputs_dif_std[i]=np.std(outputs_dif)
print(outputs_dif_avg)
print(outputs_dif_std)
generations=np.linspace(0,250,nb_measures)
#[0,62.5,125,187.5,250]
#plt.figure(figsize=(20,10))
plt.errorbar(generations,outputs_dif_avg,yerr=outputs_dif_std, color='orange',ecolor='#ffcc66')
plt.ylabel('Average output difference',fontsize='large')
plt.xlabel('Generation',fontsize='large')
plt.savefig('mutation_change.png',dpi=my_dpi)
