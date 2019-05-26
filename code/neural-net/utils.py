#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 23 15:00:15 2019

@author: cyril
"""

from functools import reduce
import torch.nn as nn
import torch
import pandas as pd
from collections import OrderedDict as OrderedDict

def comp_tot_params(model):
    tot_params = 0
    for layer in model.modules():
        if isinstance(layer, nn.LSTM) or isinstance(layer, nn.Linear):
            for param in layer.parameters():
                tot_params+=reduce(lambda x1,x2: x1*x2 ,[list(param.size())[i] for i in range(len(list(param.size())))])
    print('The model has '+str(tot_params) +' trainable parameters in total')
    #tot_th_params = 1*(4*8*50+4*50*50+8*50)+10*(4*8*10+4*10*10+8*10)+1*(150*75+75)+1*(75+1)
    return tot_params

def get_dict_sizes(state_dict, i_opp, i_gen):
    dict_sizes = {}
    all_dicts = state_dict.copy()
    all_dicts.update(i_opp), all_dicts.update(i_gen)
    for key in sorted(all_dicts.keys()):
        dict_sizes[key] = {}
        dict_sizes[key]['numel'] = all_dicts[key].numel()
        dict_sizes[key]['shape'] = list(all_dicts[key].shape)
    return dict_sizes

def get_flat_params(full_dict):
    params = torch.Tensor(0)
    for key in sorted(full_dict.keys()):
        params = torch.cat((params, full_dict[key].view(-1)),0)  
    return params

def get_full_dict(all_params, dict_sizes):
    full_dict = {}
    i_start = 0
    for layer in sorted(dict_sizes.keys()):
        full_dict[layer] = torch.Tensor(all_params[i_start:i_start+dict_sizes[layer]['numel']]).view(dict_sizes[layer]['shape'])
        i_start+=dict_sizes[layer]['numel']
    return full_dict

def get_sep_dicts(full_dict):
    state_dict = OrderedDict()
    i_opp = {}
    i_gen = {}
    for layer in sorted(full_dict.keys()):
        if layer[:3] == 'opp':
            i_opp[layer] = full_dict[layer]
        elif layer[:3] =='gen': 
            i_gen[layer] = full_dict[layer]
        else: 
            state_dict[layer] = full_dict[layer]
    return state_dict, i_opp, i_gen
    
    
    
