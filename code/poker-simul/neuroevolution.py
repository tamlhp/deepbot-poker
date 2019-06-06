#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 12:23:22 2019

@author: cyril
"""

import mkl
mkl.set_num_threads(64)
import os 
import numpy as np
import pickle
from bot_LSTMBot import LSTMBot    
import random
import torch
from sys import getsizeof
from collections import OrderedDict
from operator import add


def select_next_gen_bots(log_dir, simul_id, gen_id, all_earnings, BB, nb_bots, all_gen_flat, method = 'GA', nb_gens= 250, ini_stack=20000):
    mkl.set_num_threads(64)
    #old_gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    #creating new generation directory

    if method =='GA':
        ANEs = compute_ANE(all_earnings, BB, nb_bots, ini_stack = ini_stack)
        ord_bot_ids = [el+1 for el in sorted(range(len(ANEs)), key=lambda i:ANEs[i], reverse=True)]
        
        #for reference of layer sizes
        lstm_bot_temp = LSTMBot()
    
        #separating surviving bots
        surv_perc = 0.3
        surv_bot_ids = ord_bot_ids[:int(surv_perc*nb_bots)]  
    
        surv_bots_flat = []
        for bot_id in surv_bot_ids:
            surv_bot_flat = all_gen_flat[bot_id-1]
            surv_bots_flat.append(surv_bot_flat)
            
        surv_earnings=[0,]*len(all_earnings[0].values())
        for bot_id in surv_bot_ids:
            surv_earnings= list( map(add, surv_earnings, all_earnings[bot_id-1].values()))
            
        surv_earnings= [el/len(surv_bot_ids) for el in surv_earnings]
    
        surv_ANEs = [ANEs[i-1] for i in surv_bot_ids]
        elite_bot_ids = [id_ for id_ in surv_bot_ids if ANEs[id_-1] > sum(surv_ANEs)/float(len(surv_ANEs))]
        #print('The best bot performed:' + str(all_earnings[int(surv_bot_ids[0]-1)]))
        
        ##Preparing elite bots
        elite_bots_flat = []
        for bot_id in elite_bot_ids:
            old_el_bot_flat = all_gen_flat[bot_id-1]
            elite_bots_flat.append(old_el_bot_flat)
                
        print('Nb surviving bots: ' +str(len(surv_bot_ids))+ ', nb elite bots: '+str(len(elite_bot_ids)))
    

        repro_bots_flat = reproduce_bots(parent_bots_flat = elite_bots_flat, m_sizes_ref = lstm_bot_temp)
        next_bot_id = len(elite_bot_ids)+len(repro_bots_flat)
        mut_rate = 0.25 - 0.2*gen_id/nb_gens  ##important values
        mut_strength = 0.5 - 0.4*gen_id/nb_gens
        mutant_bots_flat = mutate_bots(orig_bots_flat = surv_bots_flat, nb_new_bots = nb_bots, ref_bot_id=next_bot_id+1, 
                                  mut_rate=mut_rate , mut_strength=mut_strength ,m_sizes_ref = lstm_bot_temp)
        
        new_gen_bots = elite_bots_flat+repro_bots_flat+mutant_bots_flat
        
    elif method=='ASE':
        pass
    return new_gen_bots, surv_earnings



def compute_ANE(all_earnings, BB, nb_bots=50, load = False, gen_dir = None, nb_opps = 4, ini_stack = 20000):
    if load:
        all_earnings = [0,]*nb_bots
        for bot_id in range (1,nb_bots+1):
            with open(gen_dir+'/bots/'+str(bot_id)+'/earnings.pkl', 'rb') as f:  
                all_earnings[bot_id-1] = pickle.load(f)
        
    earnings_arr = np.array([list(earning.values()) for earning in all_earnings])
    #set all values to positive
    earnings_arr = [list(earning + 2*ini_stack*np.ones(nb_opps)) for earning in earnings_arr]
    n_j = np.max([BB*np.ones(nb_opps),np.average(earnings_arr,axis=0)], axis=0)
    
    print('ANEs normalization factors: ' +str(n_j))
    
    return np.sum(earnings_arr/n_j, axis = 1)/nb_opps

def reproduce_bots(parent_bots_flat, m_sizes_ref):
    repro_bots = []
    new_bot_id = len(parent_bots_flat)+1
    for i in range(len(parent_bots_flat)):
        for j in range(i+1,len(parent_bots_flat)):
            first_parent = parent_bots_flat[i]
            second_parent = parent_bots_flat[j]
            child_flat_params = torch.Tensor([first_parent[k].float() if k%2==0 else second_parent[k].float() for k in range(len(first_parent))])
            repro_bots.append(child_flat_params)
            new_bot_id+=1
    return repro_bots[:25] # truncate to leave some spots for mutants

def mutate_bots(orig_bots_flat, nb_new_bots, ref_bot_id, mut_rate, mut_strength, m_sizes_ref):
    mutant_bots=[]
    for i, new_bot_id in enumerate(range(ref_bot_id, nb_new_bots+1)):
        orig_bot = orig_bots_flat[i%len(orig_bots_flat)]
        mutant_flat_params = torch.Tensor([orig_gene.float() if random.random()>mut_rate else  orig_gene.float() + random.gauss(mu=0, sigma=mut_strength) for orig_gene in orig_bot])
        mutant_bots.append(mutant_flat_params)
    return mutant_bots
    

def get_flat_params(full_dict):
    params = torch.Tensor(0)
    for key in sorted(full_dict.keys()):
        params = torch.cat((params, full_dict[key].view(-1)),0)  
    return params

def get_full_dict(all_params, m_sizes_ref):
    dict_sizes=get_dict_sizes(m_sizes_ref.state_dict,m_sizes_ref.model.i_opp,m_sizes_ref.model.i_gen)
    full_dict = OrderedDict()
    i_start = 0
    for layer in sorted(dict_sizes.keys()):
        full_dict[layer] = torch.Tensor(all_params[i_start:i_start+dict_sizes[layer]['numel']]).view(dict_sizes[layer]['shape'])
        i_start+=dict_sizes[layer]['numel']
    return full_dict


def get_dict_sizes(state_dict, i_opp, i_gen):
    dict_sizes = OrderedDict()
    all_dicts = state_dict.copy()
    all_dicts.update(i_opp), all_dicts.update(i_gen)
    for key in all_dicts.keys():
        dict_sizes[key] = {}
        dict_sizes[key]['numel'] = all_dicts[key].numel()
        dict_sizes[key]['shape'] = list(all_dicts[key].shape)
    return dict_sizes

def get_best_ANE_earnings(all_earnings, BB=100, nb_bots = 50, ini_stack=20000):
    ANEs = compute_ANE(all_earnings, BB, nb_bots, ini_stack = ini_stack)
    best_bot_id = [el for el in sorted(range(len(ANEs)), key=lambda i:ANEs[i], reverse=True)][0]
    return all_earnings[best_bot_id]
    #print('Highest ANE is ' + str(max(ANEs) )
    