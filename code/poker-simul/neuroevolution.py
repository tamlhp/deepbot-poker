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


def select_next_gen_bots(log_dir, simul_id, gen_id, all_earnings, BB, nb_bots, all_gen_dicts):
    mkl.set_num_threads(64)
    #old_gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    #creating new generation directory

    
    ANEs = compute_ANE(all_earnings, BB)
    ord_bot_ids = [el+1 for el in sorted(range(len(ANEs)), key=lambda i:ANEs[i], reverse=True)]


    #separating surviving bots
    surv_perc = 0.3
    surv_bot_ids = ord_bot_ids[:int(surv_perc*nb_bots)]  

    surv_bots_dict = []
    for bot_id in surv_bot_ids:
        #with open(old_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_dict.pkl', 'rb') as f:  
        surv_bot_dict = all_gen_dicts[bot_id-1]
        surv_bots_dict.append(surv_bot_dict)

    surv_ANEs = [ANEs[i-1] for i in surv_bot_ids]
    elite_bot_ids = [id_ for id_ in surv_bot_ids if ANEs[id_-1] > sum(surv_ANEs)/float(len(surv_ANEs))]

    print('The best bot performed:' + str(all_earnings[int(surv_bot_ids[0]-1)]))
    
    ##Preparing elite bots
    elite_bots_dict = []
    for bot_id in elite_bot_ids:
        #with open(old_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_dict.pkl', 'rb') as f:  
        old_el_bot_dict = all_gen_dicts[bot_id-1]#pickle.load(f)
            #el_bot_dict = LSTMBot(id_=i+1, gen_dir = new_gen_dir, full_dict=old_el_bot_dict)
            #print(getsizeof(el_bot_dict))
        elite_bots_dict.append(old_el_bot_dict)
            
    print('Nb surviving bots: ' +str(len(surv_bot_ids))+ ', nb elite bots: '+str(len(elite_bot_ids)))

    lstm_bot_temp = LSTMBot()
    repro_bots_dict = reproduce_bots(parent_bots_dict = elite_bots_dict, m_sizes_ref = lstm_bot_temp)
    next_bot_id = len(elite_bot_ids)+len(repro_bots_dict)
    mut_rate = 0.25 - 0.2*gen_id/nb_bots  ##important values
    mut_strength = 0.5 - 0.1*gen_id/nb_bots
    mutant_bots_dict = mutate_bots(orig_bots_dict = surv_bots_dict, nb_new_bots = nb_bots, ref_bot_id=next_bot_id+1, 
                              mut_rate=mut_rate , mut_strength=mut_strength ,m_sizes_ref = lstm_bot_temp)
    
    new_gen_bots = elite_bots_dict+repro_bots_dict+mutant_bots_dict
    return new_gen_bots



def compute_ANE(all_earnings, BB, load = False, gen_dir = None, nb_opps = 4):
    if load:
        all_earnings = [0,]*50
        for bot_id in range (1,51):
            with open(gen_dir+'/bots/'+str(bot_id)+'/earnings.pkl', 'rb') as f:  
                all_earnings[bot_id-1] = pickle.load(f)
        
    #print(earnings)
    earnings_arr = np.array([list(earning.values()) for earning in all_earnings])
    n_j = np.max([np.ones(nb_opps)*BB,np.max(earnings_arr,axis=0)], axis=0)
    
    return np.sum(earnings_arr/n_j, axis = 1)/nb_opps

def reproduce_bots(parent_bots_dict, m_sizes_ref):
    repro_bots = []
    new_bot_id = len(parent_bots_dict)+1
    for i in range(len(parent_bots_dict)):
        for j in range(i+1,len(parent_bots_dict)):
            first_parent = get_flat_params(full_dict = parent_bots_dict[i])
            second_parent = get_flat_params(full_dict = parent_bots_dict[j])
            child_flat_params = torch.Tensor([first_parent[i].float() if i%2==0 else second_parent[i].float() for i in range(len(first_parent))])
            child_full_dict = get_full_dict(all_params = child_flat_params, m_sizes_ref = m_sizes_ref)
            #child_bot = LSTMBot(id_=new_bot_id, gen_dir = new_gen_dir, full_dict=child_full_dict)
            repro_bots.append(child_full_dict)
            new_bot_id+=1
    return repro_bots[:25] # truncate to leave some spots for mutants

def mutate_bots(orig_bots_dict, nb_new_bots, ref_bot_id, mut_rate, mut_strength, m_sizes_ref):
    mutant_bots=[]
    for i, new_bot_id in enumerate(range(ref_bot_id, nb_new_bots+1)):
        orig_bot = get_flat_params(orig_bots_dict[i%len(orig_bots_dict)])
        mutant_flat_params = torch.Tensor([orig_gene.float() if random.random()>mut_rate else  orig_gene.float() + random.gauss(mu=0, sigma=mut_strength) for orig_gene in orig_bot])
        #print(mutant_flat_params[:50])
        mutant_full_dict = get_full_dict(all_params = mutant_flat_params, m_sizes_ref = m_sizes_ref)
        #mutant_bot = LSTMBot(id_=new_bot_id, gen_dir =new_gen_dir, full_dict=mutant_full_dict)
        #print(getsizeof(mutant_bot))
        mutant_bots.append(mutant_full_dict)
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
    dict_sizes = {}
    all_dicts = state_dict.copy()
    all_dicts.update(i_opp), all_dicts.update(i_gen)
    for key in sorted(all_dicts.keys()):
        dict_sizes[key] = {}
        dict_sizes[key]['numel'] = all_dicts[key].numel()
        dict_sizes[key]['shape'] = list(all_dicts[key].shape)
    return dict_sizes

def get_best_ANE_earnings(all_earnings, BB=50):
    ANEs = compute_ANE(all_earnings, BB= BB)
    best_bot_id = [el for el in sorted(range(len(ANEs)), key=lambda i:ANEs[i], reverse=True)][0]
    return all_earnings[best_bot_id]
    #print('Highest ANE is ' + str(max(ANEs) )
    